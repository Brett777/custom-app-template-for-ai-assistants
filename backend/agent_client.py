"""
Agent Deployment API client for DataRobot.

This module provides a client for calling DataRobot Agent Deployments
using the chat completions API (OpenAI-compatible format).
"""
import httpx
import json
from typing import AsyncGenerator, Optional, Union
from dataclasses import dataclass


@dataclass
class AgentMessage:
    """A message in the agent conversation."""
    role: str  # "user", "assistant", or "system"
    content: str


@dataclass
class AgentResponse:
    """Response from the agent deployment."""
    content: str
    model: str
    usage: dict
    association_id: Optional[str] = None


class AgentClient:
    """
    Client for DataRobot Agent Deployment API.

    This client provides methods to interact with deployed agents via
    the chat completions API, supporting both streaming and non-streaming
    responses.

    Example:
        client = AgentClient(
            deployment_id="abc123",
            api_token="your-token",
            endpoint="https://app.datarobot.com"
        )

        messages = [AgentMessage(role="user", content="Hello!")]
        response = await client.chat(messages)
        print(response.content)
    """

    def __init__(
        self,
        deployment_id: str,
        api_token: str,
        endpoint: str = "https://app.datarobot.com"
    ):
        """
        Initialize the agent client.

        Args:
            deployment_id: The DataRobot deployment ID for the agent
            api_token: DataRobot API token for authentication
            endpoint: DataRobot API endpoint URL
        """
        self.deployment_id = deployment_id
        self.api_token = api_token
        self.endpoint = endpoint.rstrip("/")
        self.chat_url = f"{self.endpoint}/api/v2/deployments/{deployment_id}/chat/completions"

    async def chat(
        self,
        messages: list[AgentMessage],
        stream: bool = False
    ) -> Union[AgentResponse, AsyncGenerator[str, None]]:
        """
        Send a chat request to the agent deployment.

        Args:
            messages: List of conversation messages
            stream: Whether to stream the response

        Returns:
            AgentResponse if not streaming, async generator of content chunks if streaming

        Raises:
            httpx.HTTPStatusError: If the API request fails
        """
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        payload = {
            "messages": [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ],
            "stream": stream,
        }

        if stream:
            return self._stream_response(headers, payload)
        else:
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    self.chat_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()

                return AgentResponse(
                    content=data["choices"][0]["message"]["content"],
                    model=data.get("model", "datarobot-agent"),
                    usage=data.get("usage", {}),
                    association_id=data.get("datarobot_association_id")
                )

    async def _stream_response(
        self,
        headers: dict,
        payload: dict
    ) -> AsyncGenerator[str, None]:
        """
        Stream response chunks from the agent.

        Yields content chunks as they arrive from the agent deployment.
        Uses Server-Sent Events (SSE) format.

        Args:
            headers: Request headers including authorization
            payload: Request payload with messages

        Yields:
            Content chunks as strings
        """
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                self.chat_url,
                headers=headers,
                json=payload
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
