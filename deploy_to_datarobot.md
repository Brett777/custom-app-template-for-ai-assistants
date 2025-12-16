# DataRobot Custom Application Deployment Guide

A concise guide for AI assistants building applications that deploy to DataRobot.

---

## Overview

DataRobot Custom Applications run in a containerized environment where:
- Your app is served at a **subpath**: `https://app.datarobot.com/custom_applications/{app_id}/`
- The **PORT** is provided via environment variable (typically 8080)
- Configuration is provided via **Runtime Parameters** (not .env files)
- Files are deployed in a **flat directory structure**

---

## Critical Gotchas

### 1. Base URL / Path Issues (Most Common Problem)

**Problem:** Your app works locally at `http://localhost:5173/` but breaks on DataRobot because it's served at `/custom_applications/abc123/`.

**Solution - Frontend (Vite):**
```typescript
// vite.config.ts
export default defineConfig({
  base: './',  // CRITICAL: Use relative paths, not absolute '/'
  // ...
})
```

**Solution - Dynamic Path Detection:**
```typescript
// src/lib/basePath.ts
export function getBasePath(): string {
  if (typeof window !== 'undefined') {
    const pathname = window.location.pathname;

    // Detect DataRobot custom application path
    const drMatch = pathname.match(/^(\/custom_applications\/[^/]+)/);
    if (drMatch) {
      return drMatch[1];  // Returns '/custom_applications/abc123'
    }
  }
  return '';  // Root deployment
}

export function assetPath(path: string): string {
  const base = getBasePath();
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return `${base}${normalizedPath}`;
}
```

**Usage:**
```typescript
// WRONG - breaks on DataRobot
fetch('/api/v1/config')

// CORRECT - works everywhere
fetch(assetPath('/api/v1/config'))
```

### 2. Environment Variable Naming

**Problem:** Standard `process.env.MY_VAR` doesn't work on DataRobot.

**Solution:** DataRobot prefixes runtime parameters with `MLOPS_RUNTIME_PARAM_`:
```python
# config.py
import os

def get_env(key: str, default: str = "") -> str:
    """Check MLOPS_RUNTIME_PARAM_ prefix first, fall back to standard."""
    dr_key = f"MLOPS_RUNTIME_PARAM_{key}"
    value = os.environ.get(dr_key)
    if value is not None:
        return value
    return os.environ.get(key, default)

# Usage
TRUCK_CAPACITY = int(get_env("TRUCK_CAPACITY_LBS", "45000"))
```

### 3. Startup Script Requirements

DataRobot needs a `start-app.sh` that:
- Reads PORT from environment
- Starts your server on 0.0.0.0 (not localhost)

```bash
#!/usr/bin/env sh
PORT=${PORT:-8080}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Flat Directory Structure

**Problem:** Your local structure has nested directories that don't translate to deployment.

**Solution:** Deploy a flat structure:
```
deploy/
├── main.py              # Entry point
├── config.py            # Configuration
├── requirements.txt     # Python deps
├── metadata.yaml        # Runtime parameter definitions
├── start-app.sh         # Startup script
├── frontend/
│   └── dist/            # Built React SPA
│       ├── index.html
│       └── assets/
└── data/                # Static data files
    └── *.parquet
```

### 5. Static File Path Resolution

**Problem:** Paths like `PROJECT_ROOT / "frontend" / "dist"` break in deployment.

**Solution:** Use `Path(__file__).parent` for deployment:
```python
# main.py
from pathlib import Path

# Works in flat deployment structure
APP_DIR = Path(__file__).parent
FRONTEND_DIST = APP_DIR / "frontend" / "dist"
DATA_DIR = APP_DIR / "data"
```

---

## Required Files

### metadata.yaml (Runtime Parameters)

Defines configurable parameters that users set in DataRobot UI:

```yaml
runtimeParameterDefinitions:
  - fieldName: TRUCK_CAPACITY_LBS
    type: numeric
    defaultValue: 45000
    description: Maximum truck capacity in pounds

  - fieldName: EMAIL_PASSWORD
    type: credential
    description: Email password (stored securely)
    credentialType:
      - basic

  - fieldName: DEBUG_MODE
    type: boolean
    defaultValue: false
```

**Types available:** `string`, `numeric`, `boolean`, `credential`

### start-app.sh

```bash
#!/usr/bin/env sh
echo "=== Starting Application ==="
PORT=${PORT:-8080}
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### requirements.txt

Include all Python dependencies. DataRobot uses pip to install.

---

## Backend Pattern (FastAPI)

```python
# main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

# CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path setup (flat deployment structure)
APP_DIR = Path(__file__).parent
FRONTEND_DIST = APP_DIR / "frontend" / "dist"
DATA_DIR = APP_DIR / "data"

# API routes FIRST
@app.get("/api/v1/config")
async def get_config():
    return {"status": "ok"}

@app.get("/api/v1/health")
async def health():
    return {"status": "healthy"}

# Static file mounts (specific paths before catch-all)
if DATA_DIR.exists():
    app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")

assets_dir = FRONTEND_DIST / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# SPA catch-all route LAST
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Serve specific static files
    file_path = FRONTEND_DIST / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    # Fall back to index.html for SPA routing
    return FileResponse(FRONTEND_DIST / "index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## Frontend Pattern (Vite + React)

### vite.config.ts
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  base: './',  // CRITICAL for DataRobot deployment
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8000',
      '/data': 'http://localhost:8000',
    },
  },
})
```

### API Calls Pattern
```typescript
// Always use assetPath() for API calls
import { assetPath } from '@/lib/basePath';

const response = await fetch(assetPath('/api/v1/config'));
```

---

## Deployment Script Pattern

```python
#!/usr/bin/env python
"""Deploy to DataRobot Custom Applications."""
import subprocess
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DEPLOY_DIR = PROJECT_ROOT / "deploy"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"

def build():
    # Clean deploy directory
    if DEPLOY_DIR.exists():
        shutil.rmtree(DEPLOY_DIR)
    DEPLOY_DIR.mkdir()

    # Build frontend
    subprocess.run(["npm", "run", "build"], cwd=FRONTEND_DIR, check=True)

    # Copy backend files
    for file in ["main.py", "config.py", "requirements.txt", "metadata.yaml"]:
        src = BACKEND_DIR / file
        if src.exists():
            shutil.copy(src, DEPLOY_DIR / file)

    # Copy frontend dist
    shutil.copytree(
        FRONTEND_DIR / "dist",
        DEPLOY_DIR / "frontend" / "dist"
    )

    # Copy data files
    shutil.copytree(
        PROJECT_ROOT / "data",
        DEPLOY_DIR / "data"
    )

    # Create start script
    (DEPLOY_DIR / "start-app.sh").write_text(
        "#!/usr/bin/env sh\n"
        "PORT=${PORT:-8080}\n"
        "python -m uvicorn main:app --host 0.0.0.0 --port $PORT\n"
    )

def deploy(app_name: str, env_id: str):
    subprocess.run([
        "drapps", "create",
        "--name", app_name,
        "--base-env", env_id,
        str(DEPLOY_DIR)
    ], check=True)

if __name__ == "__main__":
    # First run: drapps ls envs
    # Find an environment with Python 3.x and note its ID
    build()
    deploy("MyApp", "<YOUR_ENV_ID>")  # Get from: drapps ls envs
```

---

## drapps CLI Commands

```bash
# Install drapps
pip install git+https://github.com/datarobot/dr-apps

# Create new app
drapps create --name "MyApp" --base-env <env_id> ./deploy

# Update existing app
drapps update <app_id> ./deploy

# List apps
drapps ls apps

# View logs
drapps logs <app_name> --follow

# Terminate app
drapps terminate <app_name>
```

---

## Checklist Before Deployment

- [ ] `vite.config.ts` has `base: './'`
- [ ] All API calls use `assetPath()` helper
- [ ] `start-app.sh` reads PORT from environment
- [ ] `metadata.yaml` defines all runtime parameters
- [ ] Backend uses `MLOPS_RUNTIME_PARAM_` prefix fallback
- [ ] Static file paths use `Path(__file__).parent`
- [ ] API routes mounted BEFORE catch-all SPA route
- [ ] `requirements.txt` includes all Python dependencies
- [ ] Large static files (like WASM) are properly served

---

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| 404 on all routes | Base path mismatch | Use `base: './'` and `assetPath()` |
| API calls fail | Wrong base URL | Use `assetPath('/api/...')` |
| App doesn't start | Wrong port binding | Use `--host 0.0.0.0 --port $PORT` |
| Config not loading | Wrong env var name | Use `MLOPS_RUNTIME_PARAM_` prefix |
| Static files 404 | Wrong path resolution | Use `Path(__file__).parent` |
| SPA routes 404 | Missing catch-all | Add `/{full_path:path}` route |

---

## Finding Your Environment ID

Environment IDs are account-specific. To find available environments:

```bash
# List all available environments
drapps ls envs

# Look for an environment like:
# - "Python 3.12 Applications Base"
# - "Python 3.11 Applications Base"
# Note the ID (format: 24-character hex string like 66d07fae0513a1edf18595bb)
```

Use the environment ID when creating your app:
```bash
drapps create --name "MyApp" --base-env <env_id> ./deploy
```
