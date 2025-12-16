"""
FastAPI backend for DataRobot Custom Application.

This module serves both the API endpoints and the React SPA frontend.
"""
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings

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
