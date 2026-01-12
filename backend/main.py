"""
FastAPI backend for DataRobot Custom Application.

This module serves both the API endpoints and the React SPA frontend.
"""
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import json

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import get_settings
from agent_client import AgentClient, AgentMessage

# Initialize FastAPI app
app = FastAPI(
    title="DataRobot Custom App",
    description="Hello World template for DataRobot Custom Applications",
    version="1.0.0"
)

# CORS middleware (permissive for development; DataRobot handles auth)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path setup for flat deployment structure
APP_DIR = Path(__file__).parent
FRONTEND_DIST = APP_DIR / "frontend" / "dist"

# Load settings
settings = get_settings()


# ============================================
# API Routes (MUST be defined BEFORE SPA catch-all)
# ============================================

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/v1/config")
async def get_config():
    """
    Get application configuration.

    Returns non-sensitive configuration for the frontend.
    """
    return {
        "appTitle": settings.app_title,
        "debug": settings.debug
    }


@app.get("/api/v1/hello")
async def hello_world():
    """Hello World endpoint demonstrating basic API functionality."""
    return {
        "message": "Hello from DataRobot Custom Application!",
        "timestamp": datetime.now().isoformat()
    }


# ============================================
# Agent Chat Models
# ============================================

class ChatMessage(BaseModel):
    """A single message in the chat conversation."""
    role: str  # "user", "assistant", or "system"
    content: str


class ChatRequest(BaseModel):
    """Request body for agent chat endpoint."""
    messages: List[ChatMessage]
    stream: Optional[bool] = False


class ChatResponse(BaseModel):
    """Response from agent chat endpoint."""
    content: str
    model: str
    usage: dict


# ============================================
# Agent Chat Endpoint
# ============================================

@app.post("/api/v1/agent/chat")
async def agent_chat(request: ChatRequest):
    """
    Chat with the configured DataRobot Agent Deployment.

    This endpoint proxies chat requests to the DataRobot Agent Deployment API,
    keeping the API token secure on the server side.

    The agent deployment must be configured via:
    - AGENT_DEPLOYMENT_ID: The deployment ID from DataRobot
    - DATAROBOT_API_TOKEN: Your DataRobot API token
    - DATAROBOT_ENDPOINT: DataRobot API endpoint (default: https://app.datarobot.com)

    Args:
        request: Chat request containing messages and optional stream flag

    Returns:
        ChatResponse with agent's reply, or StreamingResponse if stream=True
    """
    # Validate configuration
    if not settings.agent_deployment_id:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Agent deployment not configured",
                "detail": "Set AGENT_DEPLOYMENT_ID in runtime parameters or environment"
            }
        )

    if not settings.datarobot_api_token:
        return JSONResponse(
            status_code=503,
            content={
                "error": "DataRobot API token not configured",
                "detail": "Set DATAROBOT_API_TOKEN in runtime parameters or environment"
            }
        )

    # Initialize agent client
    client = AgentClient(
        deployment_id=settings.agent_deployment_id,
        api_token=settings.datarobot_api_token,
        endpoint=settings.datarobot_endpoint
    )

    # Convert request messages to agent format
    messages = [
        AgentMessage(role=msg.role, content=msg.content)
        for msg in request.messages
    ]

    try:
        if request.stream:
            # Streaming response
            async def stream_generator():
                async for chunk in await client.chat(messages, stream=True):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            # Non-streaming response
            response = await client.chat(messages, stream=False)
            return ChatResponse(
                content=response.content,
                model=response.model,
                usage=response.usage
            )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Agent request failed",
                "detail": str(e)
            }
        )


@app.get("/api/v1/agent/status")
async def agent_status():
    """
    Check if agent deployment is configured and ready.

    Returns configuration status without exposing sensitive data.
    """
    return {
        "configured": bool(settings.agent_deployment_id and settings.datarobot_api_token),
        "deployment_id_set": bool(settings.agent_deployment_id),
        "api_token_set": bool(settings.datarobot_api_token),
        "endpoint": settings.datarobot_endpoint
    }


# ============================================
# LLM Gateway Models
# ============================================

class LLMMessage(BaseModel):
    """A single message for LLM Gateway."""
    role: str
    content: str


class LLMRequest(BaseModel):
    """Request body for LLM Gateway chat endpoint."""
    messages: List[LLMMessage]
    model: Optional[str] = "datarobot/azure/gpt-4o-mini"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False


# ============================================
# LLM Gateway Endpoints
# ============================================

@app.post("/api/v1/llm/chat")
async def llm_chat(request: LLMRequest):
    """
    Chat with DataRobot LLM Gateway.

    This endpoint provides direct access to LLM models through DataRobot's
    LLM Gateway, which offers unified access to multiple providers
    (Azure OpenAI, Google, Anthropic, etc.).

    Use this for simple LLM calls without agent orchestration.

    Args:
        request: LLM request containing messages, model, and parameters

    Returns:
        LLM response with content and usage stats, or StreamingResponse if stream=True
    """
    try:
        from llm_client import llm_client
    except ImportError:
        return JSONResponse(
            status_code=503,
            content={
                "error": "LLM client not available",
                "detail": "Install litellm: pip install litellm"
            }
        )

    if not llm_client.is_configured:
        return JSONResponse(
            status_code=503,
            content={
                "error": "LLM Gateway not configured",
                "detail": "Set DATAROBOT_API_TOKEN and DATAROBOT_ENDPOINT in environment"
            }
        )

    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    try:
        if request.stream:
            async def stream_generator():
                for chunk in llm_client.stream(
                    messages=messages,
                    model=request.model,
                    temperature=request.temperature
                ):
                    yield f"data: {json.dumps({'content': chunk})}\n\n"
                yield "data: [DONE]\n\n"

            return StreamingResponse(
                stream_generator(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        else:
            response = llm_client.chat(
                messages=messages,
                model=request.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            return response

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "LLM request failed",
                "detail": str(e)
            }
        )


@app.get("/api/v1/llm/models")
async def list_llm_models():
    """
    List available models in the DataRobot LLM Gateway catalog.

    Returns all models available in your DataRobot subscription.
    """
    import httpx

    if not settings.datarobot_api_token:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Not configured",
                "detail": "Set DATAROBOT_API_TOKEN in environment"
            }
        )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.datarobot_endpoint}/genai/llmgw/catalog/",
                headers={"Authorization": f"Bearer {settings.datarobot_api_token}"},
                timeout=30.0
            )

            if response.status_code == 200:
                return {"models": response.json()}
            else:
                return JSONResponse(
                    status_code=response.status_code,
                    content={
                        "error": "Failed to fetch models",
                        "detail": response.text
                    }
                )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Failed to fetch models",
                "detail": str(e)
            }
        )


@app.get("/api/v1/llm/status")
async def llm_status():
    """
    Check if LLM Gateway is configured and ready.

    Returns configuration status without exposing sensitive data.
    """
    try:
        from llm_client import llm_client, LITELLM_AVAILABLE
        is_configured = llm_client.is_configured
        litellm_available = LITELLM_AVAILABLE
    except ImportError:
        is_configured = False
        litellm_available = False

    return {
        "configured": is_configured,
        "litellm_available": litellm_available,
        "api_token_set": bool(settings.datarobot_api_token),
        "endpoint": settings.datarobot_endpoint,
        "default_model": "datarobot/azure/gpt-4o-mini"
    }


# ============================================
# Static File Serving
# ============================================

# Mount assets directory for Vite-built assets (JS, CSS, images)
assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")


# ============================================
# SPA Catch-All Route (MUST be LAST)
# ============================================

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve the React SPA.

    This catch-all route:
    1. Serves static files if they exist (e.g., favicon.ico)
    2. Falls back to index.html for client-side routing

    IMPORTANT: This route must be defined AFTER all API routes.
    """
    # Try to serve the exact file if it exists
    file_path = FRONTEND_DIST / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)

    # Fall back to index.html for SPA client-side routing
    index_path = FRONTEND_DIST / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    # If frontend not built, return error
    return JSONResponse(
        status_code=503,
        content={"error": "Frontend not built. Run 'npm run build' in frontend directory."}
    )


# ============================================
# Development Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.debug
    )
