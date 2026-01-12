"""
DataRobot LLM Gateway client using LiteLLM.

This module provides a client for interacting with DataRobot's LLM Gateway,
which offers unified access to multiple LLM providers (Azure OpenAI, Google,
Anthropic, etc.) through a single API.

Usage:
    from llm_client import llm_client

    # Simple completion
    response = llm_client.chat([
        {"role": "user", "content": "Hello!"}
    ])
    print(response["content"])

    # Streaming
    for chunk in llm_client.stream([
        {"role": "user", "content": "Tell me a story"}
    ]):
        print(chunk, end="")
"""

import os
import logging
from typing import List, Dict, Any, Optional, Generator, Union

try:
    from litellm import completion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from config import settings

logger = logging.getLogger(__name__)


def _configure_litellm():
    """Configure LiteLLM environment for DataRobot."""
    if not LITELLM_AVAILABLE:
        return

    # Set LiteLLM environment variables from settings
    if settings.datarobot_api_token:
        os.environ["DATAROBOT_API_KEY"] = settings.datarobot_api_token
    if settings.datarobot_endpoint:
        os.environ["DATAROBOT_API_BASE"] = settings.datarobot_endpoint


class LLMClient:
    """
    Client for DataRobot LLM Gateway using LiteLLM.

    Provides a simple interface for chat completions with support for
    streaming, tool calling, and multiple models.

    Attributes:
        model: Default model to use (e.g., "datarobot/azure/gpt-4o-mini")
        default_temperature: Default temperature for completions
    """

    def __init__(
        self,
        model: str = "datarobot/azure/gpt-4o-mini",
        default_temperature: float = 0.7
    ):
        """
        Initialize the LLM client.

        Args:
            model: Default model identifier in format "datarobot/<provider>/<model>"
            default_temperature: Default temperature for completions (0.0-2.0)
        """
        if not LITELLM_AVAILABLE:
            logger.warning("LiteLLM not installed. Install with: pip install litellm")

        self.model = model
        self.default_temperature = default_temperature

        # Configure LiteLLM on initialization
        _configure_litellm()

    @property
    def is_configured(self) -> bool:
        """Check if the client is properly configured."""
        return bool(
            LITELLM_AVAILABLE and
            settings.datarobot_api_token and
            settings.datarobot_endpoint
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send a chat completion request.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (overrides default)
            temperature: Temperature for completion (overrides default)
            max_tokens: Maximum tokens in response
            tools: List of tool definitions for function calling
            **kwargs: Additional arguments passed to LiteLLM

        Returns:
            Dict containing:
                - content: The assistant's response text
                - tool_calls: Any tool calls requested (if tools provided)
                - usage: Token usage statistics
                - model: Model used for completion

        Raises:
            RuntimeError: If LiteLLM is not available or not configured
        """
        if not self.is_configured:
            raise RuntimeError(
                "LLM client not configured. Ensure DATAROBOT_API_TOKEN and "
                "DATAROBOT_ENDPOINT are set, and litellm is installed."
            )

        # Build request parameters
        request_params = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            **kwargs
        }

        if max_tokens:
            request_params["max_tokens"] = max_tokens
        if tools:
            request_params["tools"] = tools

        logger.debug(f"LLM request to {request_params['model']}")

        try:
            response = completion(**request_params)

            result = {
                "content": response.choices[0].message.content,
                "tool_calls": getattr(response.choices[0].message, "tool_calls", None),
                "model": response.model,
                "finish_reason": response.choices[0].finish_reason
            }

            # Add usage if available
            if hasattr(response, "usage") and response.usage:
                result["usage"] = {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }

            return result

        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    def stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """
        Stream a chat completion response.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model to use (overrides default)
            temperature: Temperature for completion (overrides default)
            **kwargs: Additional arguments passed to LiteLLM

        Yields:
            Content chunks as they are received

        Raises:
            RuntimeError: If LiteLLM is not available or not configured
        """
        if not self.is_configured:
            raise RuntimeError(
                "LLM client not configured. Ensure DATAROBOT_API_TOKEN and "
                "DATAROBOT_ENDPOINT are set, and litellm is installed."
            )

        request_params = {
            "model": model or self.model,
            "messages": messages,
            "temperature": temperature if temperature is not None else self.default_temperature,
            "stream": True,
            **kwargs
        }

        logger.debug(f"LLM streaming request to {request_params['model']}")

        try:
            response = completion(**request_params)

            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"LLM streaming request failed: {e}")
            raise

    def chat_with_tools(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict[str, Any]],
        tool_executor: callable,
        model: Optional[str] = None,
        max_tool_calls: int = 5
    ) -> Dict[str, Any]:
        """
        Chat with automatic tool execution.

        This method handles the tool calling loop automatically:
        1. Send message to LLM with tools
        2. If LLM requests tool calls, execute them
        3. Add tool results to conversation
        4. Repeat until LLM provides final response

        Args:
            messages: Initial conversation messages
            tools: List of tool definitions
            tool_executor: Callable that takes (tool_name, arguments) and returns result
            model: Model to use (overrides default)
            max_tool_calls: Maximum number of tool call rounds to prevent infinite loops

        Returns:
            Final response dict with content and full conversation history
        """
        conversation = list(messages)
        tool_call_count = 0

        while tool_call_count < max_tool_calls:
            response = self.chat(
                messages=conversation,
                model=model,
                tools=tools
            )

            tool_calls = response.get("tool_calls")

            if not tool_calls:
                # No tool calls, return final response
                return {
                    "content": response["content"],
                    "messages": conversation,
                    "tool_calls_made": tool_call_count
                }

            # Add assistant message with tool calls
            conversation.append({
                "role": "assistant",
                "content": response["content"],
                "tool_calls": tool_calls
            })

            # Execute each tool call
            for tool_call in tool_calls:
                fn_name = tool_call.function.name
                fn_args = tool_call.function.arguments

                # Parse arguments if string
                if isinstance(fn_args, str):
                    import json
                    try:
                        fn_args = json.loads(fn_args)
                    except json.JSONDecodeError:
                        fn_args = {}

                logger.debug(f"Executing tool: {fn_name}")

                try:
                    result = tool_executor(fn_name, fn_args)
                except Exception as e:
                    result = f"Error executing tool: {str(e)}"

                # Add tool result to conversation
                conversation.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": fn_name,
                    "content": str(result) if not isinstance(result, str) else result
                })

            tool_call_count += 1

        # Max tool calls reached
        logger.warning(f"Max tool calls ({max_tool_calls}) reached")
        return {
            "content": "Maximum tool calls reached. Please try again.",
            "messages": conversation,
            "tool_calls_made": tool_call_count
        }


# Singleton instance with default configuration
llm_client = LLMClient()
