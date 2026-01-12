# DataRobot Custom Application Template

A production-ready template for building and deploying custom applications to DataRobot. This template uses **FastAPI** (Python) for the backend and **React + Vite + Tailwind CSS + shadcn/ui** for the frontend.

**Now with Agent Deployment and MCP Server integration!** Build custom UIs for AI agents powered by CrewAI, LangGraph, LlamaIndex, and more. Add custom tools via MCP (Model Context Protocol) servers.

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
│   ├── main.py              # FastAPI application with agent + LLM endpoints
│   ├── config.py            # Configuration with MLOPS_RUNTIME_PARAM_ support
│   ├── agent_client.py      # DataRobot Agent Deployment API client
│   ├── llm_client.py        # DataRobot LLM Gateway client (LiteLLM)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx          # Main React component with chat integration
│   │   ├── main.tsx         # Entry point
│   │   ├── index.css        # Tailwind CSS + CSS variables
│   │   ├── lib/
│   │   │   ├── basePath.ts  # DataRobot path helper (CRITICAL)
│   │   │   └── utils.ts     # shadcn/ui utilities
│   │   └── components/
│   │       ├── ui/          # shadcn/ui components
│   │       └── chat/        # Agent chat components
│   │           └── ChatBot.tsx  # Chat UI for agent interaction
│   ├── vite.config.ts       # Vite config (base: './' is CRITICAL)
│   ├── tailwind.config.js   # Tailwind configuration
│   └── package.json
├── deploy-config/
│   ├── start-app.sh         # DataRobot startup script
│   └── metadata.yaml        # Runtime parameter definitions
├── scripts/
│   └── deploy.py            # Build and deploy script
├── .env.example             # Environment template
├── deploy_to_datarobot.md   # Detailed deployment guide
├── AGENTS.md                # Comprehensive agent documentation
├── MCP.md                   # MCP server documentation
├── LLM_GATEWAY.md           # LLM Gateway documentation
├── UI_DESIGN.md             # UI design system documentation
├── Examples/                # Example scripts
│   ├── DataRobot_LLM_Gateway_demo.py  # LLM + MCP integration demo
│   └── check_available_models.py      # Model catalog browser
├── agent-templates/         # DataRobot Agent Templates (5 frameworks)
└── mcp-server-template/     # DataRobot MCP Server Template
```

---

## Agent Deployments Integration

This template includes integration with DataRobot Agent Deployments, enabling you to build custom UIs for AI-powered chatbots and agentic workflows.

### What are Agent Deployments?

DataRobot Agent Deployments are hosted AI agents built using frameworks like CrewAI, LangGraph, LlamaIndex, or NeMo Agent Toolkit. Once deployed, agents expose a chat completions API that your custom app can call.

### Agent Frameworks Included

The `agent-templates/` directory contains the complete [DataRobot Agent Templates](https://github.com/datarobot-community/datarobot-agent-templates):

| Framework | Best For | Location |
|-----------|----------|----------|
| **CrewAI** | Multi-agent collaboration (research teams, content creation) | `agent-templates/agent_crewai/` |
| **LangGraph** | Complex workflows with state management and branching | `agent-templates/agent_langgraph/` |
| **LlamaIndex** | RAG applications with document search and retrieval | `agent-templates/agent_llamaindex/` |
| **NeMo Agent Toolkit** | Performance-critical agents with observability | `agent-templates/agent_nat/` |
| **Generic Base** | Custom framework implementations | `agent-templates/agent_generic_base/` |

### Quick Start: Connecting to an Agent

1. **Deploy an Agent** (see `agent-templates/README.md`):
   ```bash
   cd agent-templates
   task start      # Select a framework
   task deploy     # Deploy to DataRobot
   # Save the deployment_id from output
   ```

2. **Configure Your Custom App**:
   ```bash
   # Add to .env
   AGENT_DEPLOYMENT_ID=your-deployment-id
   DATAROBOT_API_TOKEN=your-api-token
   ```

3. **Use the Chat Interface**:
   The template includes a ChatBot component that calls `/api/v1/agent/chat`.

### Example Use Cases

1. **Chatbot Interface** - Custom UI for conversational AI agents
2. **Research Assistant** - Multi-agent research with source citations
3. **Document Q&A** - RAG-powered document search with agents
4. **Workflow Automation** - UI for triggering multi-step agent tasks
5. **Analytics Dashboard** - Agent-powered data analysis and insights

See [AGENTS.md](AGENTS.md) for comprehensive documentation.

---

## MCP Server Integration

MCP (Model Context Protocol) servers enable AI agents to access external tools, APIs, and data sources. Use MCP servers to extend your agents with custom capabilities.

### What is MCP?

MCP is an open protocol that provides a standardized way for AI models to access:
- **Tools**: Functions agents can call (e.g., `get_weather`, `query_database`)
- **Resources**: Static data or context
- **Prompts**: Reusable prompt templates

### MCP Server Template

The `mcp-server-template/` directory contains the complete [DataRobot MCP Template](https://github.com/datarobot-community/datarobot-mcp-template):

```
mcp-server-template/
├── dr_mcp/                    # Main MCP application
│   ├── app/
│   │   ├── tools/             # Custom tool implementations
│   │   ├── prompts/           # Prompt templates
│   │   ├── resources/         # Static resources
│   │   └── main.py            # Entry point
│   ├── Taskfile.yaml          # Development tasks
│   └── start-app.sh           # Startup script
├── infra/                     # Pulumi deployment
└── docs/                      # Documentation
```

### Quick Start: Creating an MCP Server

1. **Set up environment:**
   ```bash
   cd mcp-server-template
   cp .env.sample dr_mcp/.env
   # Edit dr_mcp/.env with DATAROBOT_API_TOKEN and DATAROBOT_ENDPOINT
   ```

2. **Install and run locally:**
   ```bash
   task install
   cd dr_mcp && task dev
   ```

3. **Add custom tools** in `dr_mcp/app/tools/`:
   ```python
   from base import dr_mcp_tool

   @dr_mcp_tool(tags={"custom"})
   async def my_tool(param: str) -> str:
       """Tool description for the AI agent."""
       return f"Result: {param}"
   ```

4. **Deploy to DataRobot:**
   ```bash
   pulumi login --local
   cp dr_mcp/.env .env
   task deploy
   ```

### Architecture: Agent + MCP + Custom App

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Custom App    │────▶│  Agent          │────▶│  MCP Server     │
│   (React UI)    │     │  Deployment     │     │  (Tools)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

1. User interacts with Custom App
2. Custom App calls Agent Deployment
3. Agent uses MCP Server tools to fulfill requests

See [MCP.md](MCP.md) for comprehensive documentation.

---

## UI Design System

This template includes a comprehensive design system for building professional UIs that work well with DataRobot applications.

### Technology Stack

| Technology | Purpose |
|------------|---------|
| **Tailwind CSS** | Utility-first CSS framework |
| **shadcn/ui** | Accessible, customizable React components |
| **Radix UI** | Unstyled, accessible component primitives |
| **CSS Variables** | Theme tokens for consistent styling |

### Adding Components

```bash
cd frontend
npx shadcn-ui@latest add button card input dialog tabs toast
```

### Available Components

- **Form Controls**: button, input, textarea, checkbox, select, switch
- **Layout**: card, separator, scroll-area, sheet, tabs
- **Feedback**: alert, badge, progress, skeleton, toast
- **Overlay**: dialog, dropdown-menu, popover, tooltip

### Theming with CSS Variables

The design system uses HSL-based CSS variables defined in `frontend/src/index.css`:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  /* ... */
}
```

Use semantic tokens in your components:
```tsx
<div className="bg-background text-foreground">
  <button className="bg-primary text-primary-foreground">Click</button>
</div>
```

### Dark Mode Support

Toggle dark mode by adding the `dark` class to the document root:
```tsx
document.documentElement.classList.toggle('dark')
```

### Key Files

| File | Purpose |
|------|---------|
| `frontend/src/index.css` | CSS variables and Tailwind layers |
| `frontend/tailwind.config.js` | Tailwind configuration |
| `frontend/src/lib/utils.ts` | Utility functions (`cn()`) |
| `frontend/src/components/ui/` | shadcn/ui components |

See [UI_DESIGN.md](UI_DESIGN.md) for comprehensive design documentation.

---

## LLM Gateway Integration

DataRobot LLM Gateway provides unified access to multiple LLM providers (Azure OpenAI, Google, Anthropic, etc.) through a single API.

### Why Use LLM Gateway?

| Benefit | Description |
|---------|-------------|
| **Single API** | One endpoint for all LLM providers |
| **Unified Auth** | Use your DataRobot API token |
| **Model Catalog** | Browse and select available models |
| **Enterprise Security** | Centralized governance and compliance |

### Quick Start with LiteLLM

```bash
pip install litellm
```

```python
import os
from litellm import completion

# Configure
os.environ["DATAROBOT_API_KEY"] = "your-api-token"
os.environ["DATAROBOT_API_BASE"] = "https://app.datarobot.com"

# Call any model through DataRobot
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
print(response.choices[0].message.content)
```

### Available Models

Check what models are available in your catalog:

```bash
cd Examples
python check_available_models.py --all
```

Common model identifiers:
- `datarobot/azure/gpt-4o` - GPT-4o (latest)
- `datarobot/azure/gpt-4o-mini` - GPT-4o Mini (cost-effective)
- `datarobot/azure/gpt-4-turbo` - GPT-4 Turbo

### Combining with MCP Tools

LLM Gateway supports tool calling, which works great with MCP servers:

```python
# Get tools from MCP server, pass to LLM Gateway
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "What's the weather?"}],
    tools=mcp_tools  # Tools fetched from MCP server
)
```

See [LLM_GATEWAY.md](LLM_GATEWAY.md) for comprehensive documentation.

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

### Building an Agent-Powered App

When a user asks to create an AI chatbot or agent-powered application:

#### Step 1: Choose Framework
Based on requirements:
- Multi-agent collaboration → **CrewAI**
- Complex state/workflows → **LangGraph**
- Document/RAG focus → **LlamaIndex**
- Performance critical → **NeMo Agent Toolkit**
- Custom needs → **Generic Base**

#### Step 2: Create and Deploy Agent
```bash
cd agent-templates
task start      # Select framework
# Customize agent in the selected directory
task deploy     # Deploy to DataRobot
# Save the deployment_id from output
```

#### Step 3: Configure Custom App
Add to `.env`:
```bash
AGENT_DEPLOYMENT_ID=your-deployment-id
DATAROBOT_API_TOKEN=your-api-token
```

#### Step 4: Use the ChatBot Component
The template includes a ready-to-use ChatBot component at `frontend/src/components/chat/ChatBot.tsx`. It's already integrated in `App.tsx`.

#### Step 5: Customize and Deploy
Modify the frontend as needed, then deploy:
```bash
python scripts/deploy.py
```

See [AGENTS.md](AGENTS.md) for detailed agent workflow documentation.

### Building with MCP Servers

When a user needs custom tools for their AI agent:

#### Step 1: Identify Tool Requirements
- What external APIs or data sources are needed?
- What custom logic should be exposed as tools?

#### Step 2: Create MCP Server
```bash
cd mcp-server-template
cp .env.sample dr_mcp/.env
# Configure credentials
task install
```

#### Step 3: Develop Custom Tools
Create tools in `dr_mcp/app/tools/`:
```python
from base import dr_mcp_tool

@dr_mcp_tool(tags={"custom"})
async def my_tool(param: str) -> str:
    """Description for the AI agent."""
    # Your logic here
    return result
```

#### Step 4: Test Locally
```bash
cd dr_mcp && task dev              # Run server
task mcp:test-interactive          # Test with AI
```

#### Step 5: Deploy MCP Server
```bash
pulumi login --local
cp dr_mcp/.env .env
task deploy
```

#### Step 6: Connect to Agent
Configure your agent deployment to use the MCP server endpoint.

See [MCP.md](MCP.md) for detailed MCP documentation.

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
