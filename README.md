# DataRobot Custom Application Template

A production-ready template for building and deploying custom applications to DataRobot. This template uses **FastAPI** (Python) for the backend and **React + Vite + Tailwind CSS + shadcn/ui** for the frontend.

## Quick Start

### 1. Setup Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your DataRobot environment ID
# Find available environments with: drapps ls envs
```

### 2. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Local Development
```bash
# Terminal 1: Start backend (port 8000)
cd backend
python main.py

# Terminal 2: Start frontend (port 5173)
cd frontend
npm run dev
```

### 4. Deploy to DataRobot
```bash
# Install drapps CLI (first time only)
pip install git+https://github.com/datarobot/dr-apps

# Build and deploy
python scripts/deploy.py
```

---

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration with MLOPS_RUNTIME_PARAM_ support
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component
│   │   ├── main.tsx         # Entry point
│   │   ├── index.css        # Tailwind CSS + CSS variables
│   │   ├── lib/
│   │   │   ├── basePath.ts  # DataRobot path helper (CRITICAL)
│   │   │   └── utils.ts     # shadcn/ui utilities
│   │   └── components/ui/   # shadcn/ui components
│   ├── vite.config.ts       # Vite config (base: './' is CRITICAL)
│   ├── tailwind.config.js   # Tailwind configuration
│   └── package.json
├── deploy-config/
│   ├── start-app.sh         # DataRobot startup script
│   └── metadata.yaml        # Runtime parameter definitions
├── scripts/
│   └── deploy.py            # Build and deploy script
├── .env.example             # Environment template
└── deploy_to_datarobot.md   # Detailed deployment guide
```

---

## For AI Assistants

### Building a New App from This Template

When a user asks you to build a DataRobot Custom Application, follow these steps:

#### Step 1: Understand the Requirements
- What does the app need to do?
- What API endpoints are needed?
- What UI components are needed?

#### Step 2: Modify the Backend (`backend/main.py`)
```python
# Add your API endpoints BEFORE the catch-all route
@app.get("/api/v1/your-endpoint")
async def your_endpoint():
    return {"data": "your data"}

# The catch-all route for SPA MUST remain last
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # ... existing code
```

#### Step 3: Modify the Frontend (`frontend/src/App.tsx`)
```typescript
// Always use apiUrl() for API calls
import { apiUrl } from '@/lib/basePath'

const response = await fetch(apiUrl('/api/v1/your-endpoint'))
```

#### Step 4: Add Runtime Parameters (if needed)
Edit `deploy-config/metadata.yaml`:
```yaml
runtimeParameterDefinitions:
  - fieldName: YOUR_PARAM
    type: string  # string, numeric, boolean, or credential
    defaultValue: "default"
    description: "Description for DataRobot UI"
```

Access in backend via `config.py`:
```python
from config import get_env
value = get_env("YOUR_PARAM", "default")
```

#### Step 5: Deploy
```bash
python scripts/deploy.py
```

---

## Critical Patterns

### 1. Base URL Handling (MOST IMPORTANT)

DataRobot serves apps at `/custom_applications/{app_id}/`, not at root.

**Frontend - vite.config.ts:**
```typescript
export default defineConfig({
  base: './',  // CRITICAL: Use relative paths
  // ...
})
```

**Frontend - API calls:**
```typescript
// WRONG - breaks on DataRobot
fetch('/api/v1/data')

// CORRECT - works everywhere
import { apiUrl } from '@/lib/basePath'
fetch(apiUrl('/api/v1/data'))
```

### 2. Environment Variables

DataRobot prefixes runtime parameters with `MLOPS_RUNTIME_PARAM_`.

**Backend - config.py:**
```python
def get_env(key: str, default: str = "") -> str:
    # Check DataRobot runtime parameter first
    dr_key = f"MLOPS_RUNTIME_PARAM_{key}"
    value = os.environ.get(dr_key)
    if value is not None:
        return value
    return os.environ.get(key, default)
```

### 3. Server Binding

The server MUST bind to `0.0.0.0` (not `localhost`):
```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### 4. Route Order

API routes MUST be defined BEFORE the SPA catch-all:
```python
# API routes first
@app.get("/api/v1/health")
async def health(): ...

# Static mounts
app.mount("/assets", StaticFiles(...))

# SPA catch-all LAST
@app.get("/{full_path:path}")
async def serve_spa(): ...
```

### 5. Static File Paths

Use `Path(__file__).parent` for deployment compatibility:
```python
APP_DIR = Path(__file__).parent
FRONTEND_DIST = APP_DIR / "frontend" / "dist"
```

---

## Adding shadcn/ui Components

```bash
cd frontend
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
# etc.
```

Use components:
```typescript
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
```

---

## Deploy Script Usage

```bash
# Build and create new app
python scripts/deploy.py

# Build and update existing app
python scripts/deploy.py --update

# Build only (no deploy)
python scripts/deploy.py --build-only
```

The script:
1. Builds the frontend (`npm run build`)
2. Copies backend files to `deploy/`
3. Copies frontend dist to `deploy/frontend/dist/`
4. Copies startup script and metadata
5. Runs `drapps create` or `drapps publish`

---

## Configuration Files

### .env
```bash
DATAROBOT_ENV_ID=66d07fae0513a1edf18595bb  # From 'drapps ls envs'
DATAROBOT_APP_NAME=Your App Name
DATAROBOT_APP_ID=                           # Set after first deploy for updates
```

### deploy-config/metadata.yaml
```yaml
runtimeParameterDefinitions:
  - fieldName: PARAM_NAME
    type: string          # string, numeric, boolean, credential
    defaultValue: "value"
    description: "Shown in DataRobot UI"
```

### deploy-config/start-app.sh
```bash
#!/usr/bin/env sh
PORT=${PORT:-8080}
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| 404 on all routes | Base path wrong | Ensure `base: './'` in vite.config.ts |
| API calls fail | Not using apiUrl() | Use `apiUrl('/api/...')` for all fetches |
| App won't start | Wrong host binding | Use `--host 0.0.0.0` not `localhost` |
| Config not loading | Wrong env var name | Check `MLOPS_RUNTIME_PARAM_` prefix |
| Static files 404 | Path resolution | Use `Path(__file__).parent` |

---

## drapps CLI Reference

```bash
# Install
pip install git+https://github.com/datarobot/dr-apps

# List environments (to find ENV_ID)
drapps ls envs

# List apps
drapps ls apps

# Create new app
drapps create "App Name" --base-env ENV_ID --path ./deploy

# View logs
drapps logs "App Name"

# Terminate app
drapps terminate "App Name"
```

---

## Example: Building a Dashboard App

User prompt: "Create a dashboard that shows sales metrics"

AI assistant should:
1. Add API endpoint in `backend/main.py`:
   ```python
   @app.get("/api/v1/sales")
   async def get_sales():
       return {"total": 125000, "monthly": [...]}
   ```

2. Create dashboard component in `frontend/src/App.tsx`:
   ```typescript
   const [sales, setSales] = useState(null)
   useEffect(() => {
     fetch(apiUrl('/api/v1/sales'))
       .then(r => r.json())
       .then(setSales)
   }, [])
   ```

3. Add UI components:
   ```bash
   npx shadcn-ui@latest add card chart
   ```

4. Deploy:
   ```bash
   python scripts/deploy.py
   ```
