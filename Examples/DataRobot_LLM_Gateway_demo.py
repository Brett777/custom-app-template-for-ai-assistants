#!/usr/bin/env python3

import asyncio
import json
import os
import pprint
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from dotenv import load_dotenv
    from litellm import completion
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client
except ImportError:
    print("Install: pip install python-dotenv litellm mcp")
    exit(1)

# Load environment variables from backend/.env
project_root = Path(__file__).resolve().parent.parent
dotenv_path = project_root / "backend" / ".env"
if not dotenv_path.exists():
    print(f"❌ Error: .env file not found at {dotenv_path}")
    exit(1)
load_dotenv(dotenv_path=dotenv_path)

token = os.getenv("DATAROBOT_API_TOKEN")
base_url = os.getenv("DATAROBOT_API_BASE") or os.getenv("DATAROBOT_ENDPOINT")

if not token:
    raise ValueError("DATAROBOT_API_TOKEN not found")

# Configure LiteLLM
os.environ["DATAROBOT_API_KEY"] = token
os.environ["DATAROBOT_API_BASE"] = f"{base_url or 'https://app.datarobot.com'}"

# MCP Server URL - Update this to match your deployed MCP server
MCP_SERVER_URL = os.getenv("DR_MCP_SERVER_URL")
if not MCP_SERVER_URL:
    raise ValueError("DR_MCP_SERVER_URL not found in .env file. Please set it.")

async def get_available_tools() -> List[Dict[str, Any]]:
    """Get available tools from MCP server."""
    try:
        # Create MCP client with proper headers for Server-Sent Events
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }

        async with streamablehttp_client(url=MCP_SERVER_URL, headers=headers) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools_result = await session.list_tools()
                return [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                    for tool in tools_result.tools
                ]
    except Exception as e:
        print(f"❌ Failed to connect to MCP server: {e}")
        return []


async def call_mcp_tool(tool_name: str, parameters: Dict[str, Any]) -> str:
    """Call a tool on the MCP server."""
    try:
        # Create MCP client with proper headers for Server-Sent Events
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache"
        }

        async with streamablehttp_client(url=MCP_SERVER_URL, headers=headers) as (read_stream, write_stream, _):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, parameters)

                # Extract text content from the result
                if result.content and len(result.content) > 0:
                    if hasattr(result.content[0], 'text'):
                        return result.content[0].text
                    else:
                        return str(result.content[0])
                return "Tool executed successfully"
    except Exception as e:
        return f"❌ Tool call failed: {str(e)}"


async def main():
    user_question = (
        "What's the 3-day weather outlook for Ottawa, Canada?"
        " Also summarize in one paragraph after calling the tool."
    )
    messages = [
        {"role": "system", "content": "You are a helpful assistant. If tools are provided, call them when appropriate."},
        {"role": "user", "content": user_question},
    ]

    # Get available tools from MCP server
    print("🔗 Connecting to MCP server to get available tools...")
    tools = await get_available_tools()

    if not tools:
        print("❌ No tools available from MCP server. Using direct response.")
        response_stream = completion(
            model="datarobot/azure/gpt-4o-mini",
            messages=messages,
            stream=True,
        )
    else:
        print(f"✅ Found {len(tools)} tools from MCP server")

        # First, ask the model if it wants to call a tool
        first_response = completion(
            model="datarobot/azure/gpt-4o-mini",
            messages=messages,
            tools=tools,
        )

        tool_calls = getattr(first_response.choices[0].message, "tool_calls", None)

        if tool_calls:
            # Add the assistant's response to the message history.
            # This is crucial for the next call to have the context of the tool request.
            messages.append(first_response.choices[0].message)

            # Show tool call details from assistant message (non-streamed)
            print("=== TOOL CALLS (assistant request) ===")
            for tc in tool_calls:
                try:
                    name = tc.function.name  # type: ignore[attr-defined]
                    args = tc.function.arguments  # type: ignore[attr-defined]
                    tc_id = getattr(tc, "id", "N/A")
                except Exception:
                    name, args, tc_id = "N/A", "{}", "N/A"
                print(f"- id: {tc_id}, name: {name}")
                print(f"  args: {args}")

            # Process tool calls
            for call in tool_calls:
                fn_name = call.function.name  # type: ignore[attr-defined]
                fn_args_json = call.function.arguments  # type: ignore[attr-defined]

                try:
                    fn_args = json.loads(fn_args_json) if isinstance(fn_args_json, str) else fn_args_json
                except Exception:
                    fn_args = {}

                print(f"🔧 Calling MCP tool: {fn_name}")

                # Call the tool via MCP server
                tool_result = await call_mcp_tool(fn_name, fn_args)

                # Add tool result to messages
                tool_message = {
                    "role": "tool",
                    "tool_call_id": call.id,  # type: ignore[attr-defined]
                    "name": fn_name,
                    "content": tool_result,
                }
                messages.append(tool_message)

            # Stream final answer using the tool result
            response_stream = completion(
                model="datarobot/azure/gpt-4o-mini",
                messages=messages,
                stream=True,
            )
        else:
            # No tool call requested; stream a normal response
            response_stream = completion(
                model="datarobot/azure/gpt-4o-mini",
                messages=messages,
                stream=True,
            )

        # Stream and display content, collecting chunks
        print("=== STREAMING RESPONSE ===")
        full_response = ""
        chunks = []
        for chunk in response_stream:
            chunks.append(chunk)
            if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n\n=== RESPONSE METADATA ===")
        # Use the final chunk for metadata (streaming responses have limited metadata)
        final_chunk = chunks[-1] if chunks else None

        if final_chunk:
            print(f"Model: {getattr(final_chunk, 'model', 'N/A')}")
            print(f"Usage: {getattr(final_chunk, 'usage', 'N/A')}")
            print(f"Finish Reason: {final_chunk.choices[0].finish_reason}")

            # Message details from final chunk
            if hasattr(final_chunk.choices[0], 'delta'):
                delta = final_chunk.choices[0].delta
                print(f"Message Role: {getattr(delta, 'role', 'N/A')}")
                print(f"Tool Calls: {getattr(delta, 'tool_calls', 'N/A')}")
                print(f"Function Call: {getattr(delta, 'function_call', 'N/A')}")
                print(f"Annotations: {getattr(delta, 'annotations', 'N/A')}")
                print(f"Refusal: {getattr(delta, 'refusal', 'N/A')}")

        print("\n=== FULL RESPONSE CONTENT ===")
        print(full_response)


# Run the async main function
if __name__ == "__main__":
    asyncio.run(main())