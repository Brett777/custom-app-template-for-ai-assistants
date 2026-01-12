# DataRobot LLM Gateway Integration Guide

This document provides comprehensive guidance for using DataRobot's LLM Gateway in Custom Applications. The LLM Gateway provides unified access to multiple LLM providers through a single, consistent interface.

## Table of Contents
1. [Overview](#overview)
2. [Why Use LLM Gateway?](#why-use-llm-gateway)
3. [Available Models](#available-models)
4. [Getting Started](#getting-started)
5. [Using LiteLLM](#using-litellm)
6. [Direct API Access](#direct-api-access)
7. [Streaming Responses](#streaming-responses)
8. [Tool Calling](#tool-calling)
9. [Combining with MCP Servers](#combining-with-mcp-servers)
10. [Backend Integration](#backend-integration)
11. [Configuration Reference](#configuration-reference)
12. [Troubleshooting](#troubleshooting)

---

## Overview

DataRobot LLM Gateway is a unified interface that provides access to multiple LLM providers (Azure OpenAI, Google, Anthropic, etc.) through DataRobot's infrastructure. It offers:

- **Single API**: One endpoint for all LLM providers
- **Unified Authentication**: Use your DataRobot API token
- **Model Catalog**: Browse and select from available models
- **Cost Management**: Centralized billing and usage tracking
- **Governance**: Enterprise-grade security and compliance

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Custom App    │────▶│  DataRobot      │────▶│  LLM Providers  │
│   (Your Code)   │     │  LLM Gateway    │     │  (Azure, etc.)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
   LiteLLM Client        Unified API            Azure OpenAI
   or Direct HTTP        /genai/llmgw/          Google AI
                                                Anthropic
                                                And more...
```

---

## Why Use LLM Gateway?

| Benefit | Description |
|---------|-------------|
| **Simplified Access** | No need to manage multiple API keys for different providers |
| **Enterprise Security** | All requests go through DataRobot's secure infrastructure |
| **Cost Control** | Centralized billing and usage monitoring |
| **Model Flexibility** | Switch between providers without code changes |
| **Governance** | Audit trails, compliance, and access controls |
| **High Availability** | DataRobot-managed infrastructure with SLAs |

---

## Available Models

DataRobot LLM Gateway provides access to models from multiple providers:

### Checking Available Models

Use the provided script to see what models are available in your catalog:

```bash
cd Examples
python check_available_models.py              # Interactive mode
python check_available_models.py --all        # Show all models
python check_available_models.py --provider Azure  # Filter by provider
python check_available_models.py --html       # Generate HTML report
```

### Common Model Identifiers

When using LiteLLM with DataRobot, models use the format: `datarobot/<provider>/<model>`

| Provider | Model ID | Description |
|----------|----------|-------------|
| Azure OpenAI | `datarobot/azure/gpt-4o` | GPT-4o (latest) |
| Azure OpenAI | `datarobot/azure/gpt-4o-mini` | GPT-4o Mini (cost-effective) |
| Azure OpenAI | `datarobot/azure/gpt-4-turbo` | GPT-4 Turbo |
| Azure OpenAI | `datarobot/azure/gpt-35-turbo` | GPT-3.5 Turbo |
| Google | `datarobot/google/gemini-pro` | Gemini Pro |
| Anthropic | `datarobot/anthropic/claude-3-opus` | Claude 3 Opus |
| Anthropic | `datarobot/anthropic/claude-3-sonnet` | Claude 3 Sonnet |

> **Note**: Available models depend on your DataRobot subscription and configuration.

---

## Getting Started

### Prerequisites

```bash
# Install required packages
pip install litellm python-dotenv requests
```

### Environment Configuration

Add to your `backend/.env` file:

```bash
# DataRobot LLM Gateway Configuration
DATAROBOT_API_TOKEN=your-api-token
DATAROBOT_ENDPOINT=https://app.datarobot.com

# For LiteLLM compatibility
DATAROBOT_API_KEY=${DATAROBOT_API_TOKEN}
DATAROBOT_API_BASE=${DATAROBOT_ENDPOINT}
```

### Quick Test

```python
import os
from litellm import completion

# Configure LiteLLM for DataRobot
os.environ["DATAROBOT_API_KEY"] = "your-api-token"
os.environ["DATAROBOT_API_BASE"] = "https://app.datarobot.com"

# Make a request
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)

print(response.choices[0].message.content)
```

---

## Using LiteLLM

[LiteLLM](https://github.com/BerriAI/litellm) is the recommended client library for DataRobot LLM Gateway. It provides a unified interface compatible with OpenAI's API.

### Basic Usage

```python
from litellm import completion
import os

# Configure
os.environ["DATAROBOT_API_KEY"] = os.getenv("DATAROBOT_API_TOKEN")
os.environ["DATAROBOT_API_BASE"] = os.getenv("DATAROBOT_ENDPOINT", "https://app.datarobot.com")

# Simple completion
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ]
)

print(response.choices[0].message.content)
```

### With Conversation History

```python
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "My name is Alice."},
    {"role": "assistant", "content": "Hello Alice! Nice to meet you."},
    {"role": "user", "content": "What's my name?"}
]

response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=messages
)
# Response: "Your name is Alice."
```

### With Parameters

```python
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Write a haiku about coding."}],
    temperature=0.7,
    max_tokens=100,
    top_p=0.9
)
```

---

## Direct API Access

You can also call the LLM Gateway directly via HTTP:

### Chat Completions Endpoint

```python
import requests
import os

token = os.getenv("DATAROBOT_API_TOKEN")
endpoint = os.getenv("DATAROBOT_ENDPOINT", "https://app.datarobot.com")

response = requests.post(
    f"{endpoint}/genai/llmgw/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    },
    json={
        "model": "azure/gpt-4o-mini",  # Note: no "datarobot/" prefix for direct API
        "messages": [
            {"role": "user", "content": "Hello!"}
        ]
    }
)

data = response.json()
print(data["choices"][0]["message"]["content"])
```

### Model Catalog Endpoint

```python
import requests

response = requests.get(
    f"{endpoint}/genai/llmgw/catalog/",
    headers={"Authorization": f"Bearer {token}"}
)

models = response.json()
for model in models:
    print(f"- {model['model']} ({model['provider']})")
```

---

## Streaming Responses

For real-time response streaming:

### With LiteLLM

```python
from litellm import completion

response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story."}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### In FastAPI Backend

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from litellm import completion
import json

app = FastAPI()

@app.post("/api/v1/llm/chat")
async def chat(request: ChatRequest):
    if request.stream:
        return StreamingResponse(
            stream_response(request.messages),
            media_type="text/event-stream"
        )
    else:
        response = completion(
            model="datarobot/azure/gpt-4o-mini",
            messages=[m.dict() for m in request.messages]
        )
        return {"content": response.choices[0].message.content}

async def stream_response(messages):
    response = completion(
        model="datarobot/azure/gpt-4o-mini",
        messages=[m.dict() for m in messages],
        stream=True
    )

    for chunk in response:
        if chunk.choices[0].delta.content:
            yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

    yield "data: [DONE]\n\n"
```

---

## Tool Calling

LLM Gateway supports function/tool calling for models that support it:

### Define Tools

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the current weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g., 'New York'"
                    }
                },
                "required": ["location"]
            }
        }
    }
]
```

### Make Tool-Enabled Request

```python
from litellm import completion
import json

# First request - model decides to call tool
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[
        {"role": "user", "content": "What's the weather in Tokyo?"}
    ],
    tools=tools
)

# Check if model wants to call a tool
tool_calls = response.choices[0].message.tool_calls

if tool_calls:
    # Process tool calls
    messages = [
        {"role": "user", "content": "What's the weather in Tokyo?"},
        response.choices[0].message  # Include assistant's tool call request
    ]

    for tool_call in tool_calls:
        fn_name = tool_call.function.name
        fn_args = json.loads(tool_call.function.arguments)

        # Execute the tool (your implementation)
        if fn_name == "get_weather":
            result = get_weather(fn_args["location"])

        # Add tool result to messages
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "name": fn_name,
            "content": json.dumps(result)
        })

    # Get final response with tool results
    final_response = completion(
        model="datarobot/azure/gpt-4o-mini",
        messages=messages
    )

    print(final_response.choices[0].message.content)
```

---

## Combining with MCP Servers

The LLM Gateway works excellently with MCP servers for enhanced tool capabilities:

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Custom App    │────▶│  LLM Gateway    │     │  MCP Server     │
│                 │     │  (LiteLLM)      │────▶│  (Tools)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                         Tool Calling            get_weather
                         via LLM                 search_docs
                                                 custom_tools
```

### Example: LLM Gateway + MCP Tools

```python
import asyncio
from litellm import completion
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
import json

async def get_mcp_tools(mcp_url: str, token: str):
    """Fetch available tools from MCP server."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream"
    }

    async with streamablehttp_client(url=mcp_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()

            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                }
                for tool in result.tools
            ]

async def call_mcp_tool(mcp_url: str, token: str, tool_name: str, params: dict):
    """Execute a tool on the MCP server."""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "text/event-stream"
    }

    async with streamablehttp_client(url=mcp_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, params)

            if result.content and hasattr(result.content[0], 'text'):
                return result.content[0].text
            return str(result.content[0])

async def chat_with_tools(user_message: str, mcp_url: str, token: str):
    """Chat using LLM Gateway with MCP tools."""

    # Get available tools from MCP server
    tools = await get_mcp_tools(mcp_url, token)

    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when appropriate."},
        {"role": "user", "content": user_message}
    ]

    # First LLM call - may request tool use
    response = completion(
        model="datarobot/azure/gpt-4o-mini",
        messages=messages,
        tools=tools
    )

    tool_calls = response.choices[0].message.tool_calls

    if tool_calls:
        messages.append(response.choices[0].message)

        # Execute each tool call via MCP
        for call in tool_calls:
            fn_name = call.function.name
            fn_args = json.loads(call.function.arguments)

            result = await call_mcp_tool(mcp_url, token, fn_name, fn_args)

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "name": fn_name,
                "content": result
            })

        # Final LLM call with tool results
        response = completion(
            model="datarobot/azure/gpt-4o-mini",
            messages=messages,
            stream=True
        )

        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        return full_response
    else:
        return response.choices[0].message.content

# Usage
asyncio.run(chat_with_tools(
    "What's the weather in Ottawa?",
    mcp_url="https://your-mcp-server.datarobot.com/mcp/",
    token="your-api-token"
))
```

---

## Backend Integration

### Adding LLM Gateway to Your Custom App

#### 1. Update Requirements

Add to `backend/requirements.txt`:

```
litellm>=1.0.0
```

#### 2. Create LLM Client

Create `backend/llm_client.py`:

```python
"""DataRobot LLM Gateway client using LiteLLM."""

import os
from typing import List, Dict, Any, Optional, Generator
from litellm import completion
from config import settings

# Configure LiteLLM for DataRobot
os.environ["DATAROBOT_API_KEY"] = settings.datarobot_api_token
os.environ["DATAROBOT_API_BASE"] = settings.datarobot_endpoint


class LLMClient:
    """Client for DataRobot LLM Gateway."""

    def __init__(self, model: str = "datarobot/azure/gpt-4o-mini"):
        self.model = model

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Send a chat completion request."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens
        if tools:
            kwargs["tools"] = tools

        response = completion(**kwargs)

        return {
            "content": response.choices[0].message.content,
            "tool_calls": getattr(response.choices[0].message, "tool_calls", None),
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }

    def stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """Stream a chat completion response."""
        response = completion(
            model=self.model,
            messages=messages,
            temperature=temperature,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
llm_client = LLMClient()
```

#### 3. Add API Endpoint

Add to `backend/main.py`:

```python
from pydantic import BaseModel
from typing import List, Optional
from fastapi.responses import StreamingResponse
from llm_client import llm_client
import json

class LLMMessage(BaseModel):
    role: str
    content: str

class LLMRequest(BaseModel):
    messages: List[LLMMessage]
    model: Optional[str] = "datarobot/azure/gpt-4o-mini"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False

@app.post("/api/v1/llm/chat")
async def llm_chat(request: LLMRequest):
    """Chat with DataRobot LLM Gateway."""
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    if request.stream:
        async def generate():
            for chunk in llm_client.stream(messages, request.temperature):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        result = llm_client.chat(
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        return result

@app.get("/api/v1/llm/models")
async def list_models():
    """List available models in the catalog."""
    import requests

    response = requests.get(
        f"{settings.datarobot_endpoint}/genai/llmgw/catalog/",
        headers={"Authorization": f"Bearer {settings.datarobot_api_token}"}
    )

    if response.status_code == 200:
        return {"models": response.json()}
    else:
        return {"error": "Failed to fetch models", "status": response.status_code}
```

#### 4. Frontend Integration

```typescript
import { apiUrl } from '@/lib/basePath'

interface LLMResponse {
  content: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

async function chatWithLLM(messages: Array<{role: string, content: string}>): Promise<LLMResponse> {
  const response = await fetch(apiUrl('/api/v1/llm/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
      model: 'datarobot/azure/gpt-4o-mini',
      temperature: 0.7
    })
  });

  return response.json();
}

// Streaming example
async function streamLLMResponse(
  messages: Array<{role: string, content: string}>,
  onChunk: (content: string) => void
): Promise<void> {
  const response = await fetch(apiUrl('/api/v1/llm/chat'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      messages,
      stream: true
    })
  });

  const reader = response.body?.getReader();
  const decoder = new TextDecoder();

  while (reader) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value);
    const lines = chunk.split('\n').filter(line => line.startsWith('data: '));

    for (const line of lines) {
      const data = line.slice(6); // Remove "data: "
      if (data === '[DONE]') return;

      try {
        const parsed = JSON.parse(data);
        if (parsed.content) {
          onChunk(parsed.content);
        }
      } catch (e) {
        // Skip invalid JSON
      }
    }
  }
}
```

---

## Configuration Reference

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATAROBOT_API_TOKEN` | DataRobot API token | Yes |
| `DATAROBOT_ENDPOINT` | DataRobot instance URL | Yes |
| `DATAROBOT_API_KEY` | Alias for API token (LiteLLM) | Auto-set |
| `DATAROBOT_API_BASE` | Alias for endpoint (LiteLLM) | Auto-set |

### LiteLLM Model Format

```
datarobot/<provider>/<model-name>

Examples:
- datarobot/azure/gpt-4o-mini
- datarobot/azure/gpt-4o
- datarobot/google/gemini-pro
- datarobot/anthropic/claude-3-sonnet
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/genai/llmgw/catalog/` | GET | List available models |
| `/genai/llmgw/v1/chat/completions` | POST | Chat completions |
| `/genai/llmgw/v1/embeddings` | POST | Text embeddings |

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid API token | Verify `DATAROBOT_API_TOKEN` |
| 404 Not Found | Wrong endpoint | Check `DATAROBOT_ENDPOINT` format |
| Model not found | Model not in catalog | Run `check_available_models.py` |
| Connection timeout | Network issue | Check firewall/proxy settings |
| Rate limited | Too many requests | Implement backoff/retry logic |

### Debugging Tips

1. **Check credentials**:
   ```python
   import os
   print(f"Token: {os.getenv('DATAROBOT_API_TOKEN')[:10]}...")
   print(f"Endpoint: {os.getenv('DATAROBOT_ENDPOINT')}")
   ```

2. **Test API connectivity**:
   ```bash
   curl -H "Authorization: Bearer $DATAROBOT_API_TOKEN" \
        "$DATAROBOT_ENDPOINT/genai/llmgw/catalog/"
   ```

3. **Enable LiteLLM logging**:
   ```python
   import litellm
   litellm.set_verbose = True
   ```

4. **Check available models**:
   ```bash
   python Examples/check_available_models.py --all
   ```

---

## For AI Assistants

When building applications that need LLM capabilities:

### Decision Tree

1. **Need agent with tools?** → Use Agent Deployment + MCP Server
2. **Need simple LLM calls?** → Use LLM Gateway directly
3. **Need both?** → Combine LLM Gateway with MCP tools

### Quick Implementation

1. Add `litellm` to requirements
2. Configure environment variables
3. Create `llm_client.py` with the `LLMClient` class
4. Add `/api/v1/llm/chat` endpoint
5. Call from frontend using `apiUrl()`

### Best Practices

- Use streaming for long responses
- Implement proper error handling
- Cache model catalog results
- Use appropriate models for tasks (mini for simple, full for complex)
- Monitor token usage for cost control

---

## Resources

- [LiteLLM Documentation](https://docs.litellm.ai/)
- [DataRobot Documentation](https://docs.datarobot.com/)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) (compatible format)
- [Example Scripts](Examples/) - Working examples in this repository
