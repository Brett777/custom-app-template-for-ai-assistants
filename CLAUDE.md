# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DataRobot Custom Application template using FastAPI (Python) backend + React/Vite/Tailwind frontend with **DataRobot UI (dr-ui)** as the primary component library. Apps deploy to DataRobot's containerized environment at subpaths like `/custom_applications/{app_id}/`.

**IMPORTANT: Use DataRobot UI (dr-ui) as the default component library for all UI development unless explicitly stated otherwise.** dr-ui extends shadcn/ui with DataRobot-specific components, theming, and features like production-ready chat interfaces.

## Common Commands

### Local Development
```bash
# Backend (terminal 1, port 8000)
cd backend && pip install -r requirements.txt && python main.py

# Frontend (terminal 2, port 5173)
cd frontend && npm install && npm run dev
```

### Build & Deploy
```bash
python scripts/deploy.py              # Build and create new app
python scripts/deploy.py --update     # Update existing app
python scripts/deploy.py --build-only # Build only (creates deploy/ folder)
```

### Frontend Tasks
```bash
cd frontend
npm run build       # TypeScript compile + Vite build
npm run lint        # ESLint
npx shadcn@latest add @dr-ui/<component>  # Add dr-ui components (preferred)
npx shadcn-ui@latest add <component>      # Add shadcn/ui components (fallback)
```

### drapps CLI
```bash
pip install git+https://github.com/datarobot/dr-apps  # Install
drapps ls envs      # List available environments (to get ENV_ID)
drapps ls apps      # List deployed apps
drapps logs "AppName" --follow  # View logs
```

## Architecture

### Deployment Structure
The deploy script (`scripts/deploy.py`) creates a flat `deploy/` directory:
```
deploy/
├── main.py, config.py, agent_client.py   # Backend copied from backend/
├── requirements.txt                       # Python dependencies
├── metadata.yaml, start-app.sh           # Copied from deploy-config/
└── frontend/dist/                        # Built React SPA
```

### Critical Patterns

**1. Base URL Handling** - DataRobot serves at `/custom_applications/{app_id}/`, not root:
- `vite.config.ts`: Must use `base: './'` for relative paths
- Frontend API calls: Always use `apiUrl()` from `@/lib/basePath.ts`
```typescript
import { apiUrl } from '@/lib/basePath'
fetch(apiUrl('/api/v1/endpoint'))  // NOT fetch('/api/v1/endpoint')
```

**2. Environment Variables** - DataRobot prefixes runtime params with `MLOPS_RUNTIME_PARAM_`:
```python
from config import get_env
value = get_env("YOUR_PARAM", "default")  # Checks MLOPS_RUNTIME_PARAM_YOUR_PARAM first
```

**3. Route Order in main.py** - API routes BEFORE SPA catch-all:
```python
@app.get("/api/v1/...")  # API routes first
app.mount("/assets", ...)  # Static mounts
@app.get("/{full_path:path}")  # SPA catch-all LAST
```

**4. Server Binding** - Must use `0.0.0.0` (not localhost) for DataRobot

### Key Files
- `backend/config.py`: Settings class with `get_env()` helper for DataRobot runtime params
- `frontend/src/lib/basePath.ts`: `apiUrl()` and `assetPath()` for correct URL construction
- `deploy-config/metadata.yaml`: Runtime parameter definitions for DataRobot UI
- `deploy-config/start-app.sh`: Container startup script (reads PORT from env)
- `.env.example`: Template for local development config

### Configuration
Set `DATAROBOT_ENV_ID` in `.env` before deploying (get from `drapps ls envs`). Add custom runtime parameters to both `.env` (local) and `deploy-config/metadata.yaml` (DataRobot).

## Agent Deployment Integration

### Agent Templates Location
The complete DataRobot Agent Templates repository is at `agent-templates/`. This contains 5 frameworks for building AI agents.

### Common Agent Commands
```bash
# Navigate to agent templates
cd agent-templates

# Initialize a new agent (interactive)
task start

# Run agent locally for testing
task agent:cli START_DEV=1 -- execute --user_prompt "Your prompt here"

# Deploy agent to DataRobot
task deploy

# Test deployed agent
task agent:cli -- execute-deployment --deployment_id <ID> --user_prompt "Test"
```

### Agent Framework Selection
| User Need | Framework |
|-----------|-----------|
| Multi-agent collaboration | **CrewAI** (`agent_crewai/`) |
| Complex workflows with state | **LangGraph** (`agent_langgraph/`) |
| Document search / RAG | **LlamaIndex** (`agent_llamaindex/`) |
| Performance monitoring | **NeMo Agent Toolkit** (`agent_nat/`) |
| Custom framework | **Generic Base** (`agent_generic_base/`) |

### Connecting App to Agent Deployment

1. **Configure environment** (`.env`):
```bash
AGENT_DEPLOYMENT_ID=<deployment-id-from-task-deploy>
DATAROBOT_API_TOKEN=<your-api-token>
DATAROBOT_ENDPOINT=https://app.datarobot.com
```

2. **Use the ChatBot component** - Already integrated in `frontend/src/App.tsx`

3. **Backend endpoints available**:
   - `POST /api/v1/agent/chat` - Chat with agent
   - `GET /api/v1/agent/status` - Check agent configuration

### Key Files for Agent Integration
- `agent-templates/`: Complete agent frameworks and templates
- `backend/agent_client.py`: API client for calling agent deployments
- `backend/main.py`: Includes `/api/v1/agent/chat` endpoint
- `frontend/src/components/chat/ChatBot.tsx`: Chat UI component
- `AGENTS.md`: Comprehensive agent documentation
- `deploy-config/metadata.yaml`: Runtime parameters including AGENT_DEPLOYMENT_ID

## MCP Server Integration

### MCP Template Location
The complete DataRobot MCP Server template is at `mcp-server-template/`. This provides a framework for building MCP servers with custom tools.

### Common MCP Commands
```bash
# Navigate to MCP template
cd mcp-server-template

# Install dependencies
task install

# Run MCP server locally
cd dr_mcp && task dev

# Test tools interactively with AI
task mcp:test-interactive

# Deploy to DataRobot
pulumi login --local
cp dr_mcp/.env .env
task deploy

# Get deployment info
task infra:info

# Destroy deployment
task destroy
```

### Creating Custom Tools
Add tools in `mcp-server-template/dr_mcp/app/tools/`:

```python
from base import dr_mcp_tool

@dr_mcp_tool(tags={"custom", "example"})
async def my_custom_tool(param: str, optional: int = 10) -> str:
    """
    Brief description of what the tool does.

    Args:
        param: Required parameter description
        optional: Optional parameter description

    Returns:
        Description of return value
    """
    # Your logic here
    return f"Result: {param}"
```

### Tool Best Practices
| Practice | Description |
|----------|-------------|
| Docstrings | LLMs use these to understand when to use the tool |
| Type Hints | Required for all parameters and return values |
| Async | Tools must be async functions |
| Error Handling | Return JSON error messages |
| Tags | Categorize tools for filtering |

### MCP Server Structure
```
mcp-server-template/dr_mcp/app/
├── tools/           # Custom tool implementations
├── prompts/         # Prompt templates
├── resources/       # Static resources
├── core/            # Configuration and lifecycle
└── main.py          # Entry point
```

### Key Files for MCP Integration
- `mcp-server-template/`: Complete MCP server framework
- `mcp-server-template/dr_mcp/app/tools/`: Custom tool implementations
- `mcp-server-template/dr_mcp/.env`: Environment configuration
- `mcp-server-template/infra/`: Pulumi deployment configuration
- `MCP.md`: Comprehensive MCP documentation

### Architecture: Agent + MCP + Custom App
```
Custom App → Agent Deployment → MCP Server
(React UI)   (AI with tools)    (Tools/APIs)
```

For full-stack AI apps:
1. Create MCP server with custom tools
2. Deploy MCP server to DataRobot
3. Create agent configured to use MCP server
4. Deploy agent to DataRobot
5. Configure Custom App with agent deployment ID

## UI Design System

### Default Component Library: DataRobot UI (dr-ui)

**ALWAYS use DataRobot UI (dr-ui) as the primary component library unless explicitly stated otherwise.**

[dr-ui](https://dr-ui.datarobot.com/) is DataRobot's open-source React component library that extends shadcn/ui with:
- **Chat Components**: Production-ready chat interfaces with `use-chat` hook
- **DataRobot Theming**: Consistent look and feel with DataRobot products
- **Accessibility**: Built on Radix UI primitives
- **i18n Support**: Multiple language locales
- **Dark Mode**: Flexible theming system

### Technology Stack
| Technology | Purpose |
|------------|---------|
| **DataRobot UI (dr-ui)** | Primary component library (DEFAULT) |
| **Tailwind CSS** | Utility-first CSS framework |
| **shadcn/ui** | Base components (extended by dr-ui) |
| **Radix UI** | Accessible component primitives |
| **CSS Variables** | HSL-based theme tokens |

### Installing dr-ui Components
```bash
cd frontend

# Configure components.json to use dr-ui registry, then:
npx shadcn@latest add @dr-ui/button
npx shadcn@latest add @dr-ui/chat
npx shadcn@latest add @dr-ui/card
```

### Installing shadcn/ui Components (fallback)
Use shadcn/ui directly only when dr-ui doesn't have the component:
```bash
cd frontend
npx shadcn-ui@latest add dialog tabs toast badge scroll-area
```

### Chat Interface (dr-ui)
dr-ui provides production-ready chat components - **always use these for chat UIs**:
```tsx
import { Chat, ChatMessage, ChatInput } from '@dr-ui/chat'
import { useChat } from '@dr-ui/hooks'

function ChatInterface() {
  const { messages, sendMessage, isLoading } = useChat({
    endpoint: '/api/v1/agent/chat'
  })

  return (
    <Chat>
      {messages.map(msg => (
        <ChatMessage key={msg.id} role={msg.role}>
          {msg.content}
        </ChatMessage>
      ))}
      <ChatInput onSend={sendMessage} disabled={isLoading} />
    </Chat>
  )
}
```

### Component Usage
```tsx
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'

// Use semantic color tokens
<div className="bg-background text-foreground">
  <Button variant="primary">Click</Button>
  <Button variant="secondary">Cancel</Button>
  <Button variant="destructive">Delete</Button>
</div>
```

### CSS Variable Tokens
Key tokens defined in `frontend/src/index.css`:
| Token | Usage |
|-------|-------|
| `--background` | Page background |
| `--foreground` | Main text color |
| `--primary` | Primary actions, buttons |
| `--secondary` | Secondary actions |
| `--muted` | Disabled states, subtle elements |
| `--destructive` | Errors, delete actions |
| `--border` | Borders, dividers |

### Class Merging with `cn()`
```tsx
import { cn } from '@/lib/utils'

<div className={cn(
  "px-4 py-2 rounded-md",
  isActive && "bg-primary text-primary-foreground",
  className
)}>
```

### Dark Mode
```tsx
// Toggle dark mode
document.documentElement.classList.toggle('dark')
```

### Key Files for UI
| File | Purpose |
|------|---------|
| `frontend/src/index.css` | CSS variables, Tailwind config |
| `frontend/src/lib/utils.ts` | `cn()` utility for class merging |
| `frontend/src/components/ui/` | dr-ui and shadcn/ui components |
| `frontend/src/components/chat/` | Chat UI components |
| `UI_DESIGN.md` | Comprehensive design documentation |

### Component Selection Priority
1. **dr-ui component** - Use if available (chat, buttons, cards, etc.)
2. **shadcn/ui component** - Use if dr-ui doesn't have it
3. **Custom component** - Build only when necessary, follow dr-ui patterns

### Component Checklist
When creating UI components, ensure:
- [ ] Uses dr-ui components when available
- [ ] Uses Tailwind utility classes (not custom CSS)
- [ ] Uses CSS variable tokens for colors
- [ ] Has TypeScript types
- [ ] Handles loading states
- [ ] Handles error states
- [ ] Keyboard accessible
- [ ] Works in dark mode

## LLM Gateway Integration

### Overview
DataRobot LLM Gateway provides unified access to multiple LLM providers (Azure OpenAI, Google, Anthropic) through a single API using LiteLLM.

### Quick Setup
```bash
pip install litellm
```

```python
import os
from litellm import completion

os.environ["DATAROBOT_API_KEY"] = os.getenv("DATAROBOT_API_TOKEN")
os.environ["DATAROBOT_API_BASE"] = os.getenv("DATAROBOT_ENDPOINT")

response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### Model Format
```
datarobot/<provider>/<model-name>

Examples:
- datarobot/azure/gpt-4o-mini    # Cost-effective
- datarobot/azure/gpt-4o         # Latest GPT-4
- datarobot/azure/gpt-4-turbo    # GPT-4 Turbo
```

### Check Available Models
```bash
cd Examples
python check_available_models.py --all      # List all models
python check_available_models.py --provider Azure  # Filter by provider
```

### Streaming Responses
```python
response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Tell me a story"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
```

### Tool Calling
```python
tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {"location": {"type": "string"}},
            "required": ["location"]
        }
    }
}]

response = completion(
    model="datarobot/azure/gpt-4o-mini",
    messages=[{"role": "user", "content": "Weather in Tokyo?"}],
    tools=tools
)
```

### LLM Gateway + MCP Server Pattern
```
Custom App → LLM Gateway → MCP Server
             (LiteLLM)     (Tools)
```

1. Fetch tools from MCP server
2. Pass tools to LLM Gateway completion call
3. Execute tool calls via MCP server
4. Return results to LLM for final response

### Key Files for LLM Gateway
| File | Purpose |
|------|---------|
| `Examples/DataRobot_LLM_Gateway_demo.py` | Full demo with MCP integration |
| `Examples/check_available_models.py` | Model catalog browser |
| `backend/llm_client.py` | LLM Gateway client (if created) |
| `LLM_GATEWAY.md` | Comprehensive documentation |

### When to Use What
| Need | Solution |
|------|----------|
| Simple LLM calls | LLM Gateway directly |
| Agent with conversation | Agent Deployment |
| Custom tools | MCP Server |
| LLM + tools (no agent) | LLM Gateway + MCP |
| Full agent system | Agent Deployment + MCP |
