# DataRobot Agent Deployments Integration Guide

This document provides comprehensive guidance for AI assistants and developers working with DataRobot Agent Deployments in Custom Applications.

## Table of Contents
1. [Overview](#overview)
2. [Agent Frameworks](#agent-frameworks)
3. [Creating an Agent Deployment](#creating-an-agent-deployment)
4. [Deploying the Agent](#deploying-the-agent)
5. [Connecting Custom App to Agent](#connecting-custom-app-to-agent)
6. [Testing the Integration](#testing-the-integration)
7. [API Reference](#api-reference)
8. [Troubleshooting](#troubleshooting)

---

## Overview

DataRobot Agent Deployments are hosted AI agents that expose an OpenAI-compatible chat completions API. This template enables you to:

1. Build agents using 5 different frameworks
2. Deploy agents to DataRobot infrastructure
3. Connect custom web applications to deployed agents
4. Create rich conversational UIs

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   React UI      │────▶│  FastAPI        │────▶│  DataRobot      │
│   (ChatBot)     │     │  Backend        │     │  Agent Deploy   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
   User Input         /api/v1/agent/chat      /api/v2/deployments/
                      (Proxy endpoint)         {id}/chat/completions
```

**Why proxy through backend?**
- Keeps API token secure (never exposed to frontend)
- Allows request/response transformation
- Enables logging and error handling
- Works with DataRobot's credential system

---

## Agent Frameworks

The `agent-templates/` directory contains ready-to-use templates for 5 frameworks:

### CrewAI (`agent-templates/agent_crewai/`)

**Best for**: Multi-agent collaboration where specialized agents work together.

**Key Concepts**:
- Agents have defined roles, goals, and tools
- Tasks are assigned to specific agents
- Agents collaborate to complete complex workflows

**Example Use Cases**:
- Research team (Researcher + Writer agents)
- Customer service (Classifier + Responder agents)
- Content creation (Researcher + Editor + Publisher)

### LangGraph (`agent-templates/agent_langgraph/`)

**Best for**: Complex workflows requiring state management, branching, and loops.

**Key Concepts**:
- Graph-based workflow definition
- Explicit state management
- Conditional routing and human-in-the-loop

**Example Use Cases**:
- Approval workflows
- Multi-step analysis with checkpoints
- Decision trees with fallback paths

### LlamaIndex (`agent-templates/agent_llamaindex/`)

**Best for**: RAG (Retrieval Augmented Generation) applications with document search.

**Key Concepts**:
- Document indexing and retrieval
- Semantic search over knowledge bases
- Query engines with specialized tools

**Example Use Cases**:
- Documentation assistants
- Knowledge base Q&A
- Research assistants with source citations

### NeMo Agent Toolkit (`agent-templates/agent_nat/`)

**Best for**: Performance-critical applications requiring observability.

**Key Concepts**:
- NVIDIA NeMo integration
- Performance profiling
- Cost monitoring and optimization

**Example Use Cases**:
- Production agents with SLA requirements
- High-throughput applications
- Agents requiring detailed telemetry

### Generic Base (`agent-templates/agent_generic_base/`)

**Best for**: Custom implementations using other frameworks or approaches.

**Key Concepts**:
- Minimal boilerplate
- Framework-agnostic structure
- Full customization freedom

**Example Use Cases**:
- Custom agent frameworks
- Hybrid approaches
- Specialized use cases

---

## Creating an Agent Deployment

### Prerequisites

**Required Tools** (macOS/Linux only, use WSL on Windows):
- git (>=2.30.0)
- uv package manager (>=0.6.10)
- Pulumi (>=3.163.0)
- Taskfile (>=3.43.3)

### Step 1: Set Up Environment

```bash
# Navigate to agent templates
cd agent-templates

# Copy environment template
cp .env.template .env

# Edit .env with your DataRobot credentials
# DATAROBOT_API_TOKEN=your-api-token
# DATAROBOT_ENDPOINT=https://app.datarobot.com
```

### Step 2: Select and Initialize Framework

```bash
# Interactive framework selection
task start

# This will:
# 1. Prompt you to select a framework
# 2. Initialize the selected template
# 3. Set up Python dependencies with uv
```

### Step 3: Customize Your Agent

Each framework has a similar structure:

```
agent_crewai/
├── agents/           # Agent definitions
├── tasks/            # Task definitions
├── tools/            # Custom tools
├── workflows/        # Workflow orchestration
└── pyproject.toml    # Dependencies
```

Modify the agents, tasks, and tools to match your requirements.

### Step 4: Test Locally

```bash
# Run agent locally with a test prompt
task agent:cli START_DEV=1 -- execute --user_prompt "Your test prompt"
```

---

## Deploying the Agent

### Step 1: Configure Pulumi

```bash
# Login to Pulumi (local or cloud)
pulumi login --local  # Or pulumi login for cloud

# Set your stack name
export PULUMI_STACK_NAME=my-agent
```

### Step 2: Deploy

```bash
task deploy
```

This will:
1. Package your agent code
2. Create a custom model in DataRobot
3. Deploy the model
4. Create a chat endpoint

### Step 3: Capture Deployment Info

After deployment, save these values:

```
Deployment ID: xxxxxxxxxxxxxxxxxxxxxxxx
Custom Model Chat Endpoint: https://app.datarobot.com/api/v2/genai/agents/fromCustomModel/xxx/chat/
Deployment Chat Endpoint: https://app.datarobot.com/api/v2/deployments/xxx/chat/completions
Agent Playground URL: https://app.datarobot.com/...
```

**Important**: Copy the Deployment ID - you'll need it to configure your Custom App.

---

## Connecting Custom App to Agent

### Step 1: Configure Runtime Parameters

The template already includes agent parameters in `deploy-config/metadata.yaml`:

```yaml
- fieldName: AGENT_DEPLOYMENT_ID
  type: string
  description: "DataRobot Agent Deployment ID"

- fieldName: DATAROBOT_API_TOKEN
  type: credential
  description: "DataRobot API Token"
  credentialType:
    - api_token

- fieldName: DATAROBOT_ENDPOINT
  type: string
  defaultValue: "https://app.datarobot.com"
  description: "DataRobot API endpoint"
```

### Step 2: Local Development

For local testing, set these in your `.env` file:

```bash
AGENT_DEPLOYMENT_ID=your-deployment-id
DATAROBOT_API_TOKEN=your-api-token
DATAROBOT_ENDPOINT=https://app.datarobot.com
```

### Step 3: Deploy Custom App

When deploying to DataRobot, configure these parameters in the Custom App settings UI.

---

## Testing the Integration

### Local Testing

1. Start the backend:
   ```bash
   cd backend && python main.py
   ```

2. Start the frontend:
   ```bash
   cd frontend && npm run dev
   ```

3. Navigate to the chat interface and test.

### Testing Deployed App

1. Deploy the custom app:
   ```bash
   python scripts/deploy.py
   ```

2. Configure runtime parameters in DataRobot UI:
   - Set AGENT_DEPLOYMENT_ID
   - Add DATAROBOT_API_TOKEN credential
   - Set DATAROBOT_ENDPOINT if needed

3. Start the application and test the chat interface.

### Testing Agent Directly

You can test the agent deployment directly via curl:

```bash
curl -X POST "${DATAROBOT_ENDPOINT}/api/v2/deployments/${DEPLOYMENT_ID}/chat/completions" \
  -H "Authorization: Bearer ${API_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Hello, how can you help me?"}
    ]
  }'
```

---

## API Reference

### Backend Endpoints

#### POST /api/v1/agent/chat

Chat with the configured agent deployment.

**Request Body**:
```json
{
  "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

**Response** (non-streaming):
```json
{
  "content": "Hello! How can I help you today?",
  "model": "datarobot-agent",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  }
}
```

**Streaming Response** (when `stream: true`):
```
data: {"content": "Hello"}
data: {"content": "!"}
data: {"content": " How"}
data: [DONE]
```

#### GET /api/v1/agent/status

Check agent configuration status.

**Response**:
```json
{
  "configured": true,
  "deployment_id_set": true,
  "api_token_set": true,
  "endpoint": "https://app.datarobot.com"
}
```

### DataRobot Agent API

The backend proxies to DataRobot's chat completions API:

**URL**: `POST /api/v2/deployments/{deployment_id}/chat/completions`

**Headers**:
```
Authorization: Bearer <api_token>
Content-Type: application/json
```

**Request Body**:
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": false
}
```

**Response** (OpenAI-compatible format):
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1699000000,
  "model": "datarobot-deployed-llm",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Hello! How can I help you today?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 8,
    "total_tokens": 18
  },
  "datarobot_association_id": "xxx"
}
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid API token | Verify DATAROBOT_API_TOKEN is correct |
| 404 Not Found | Wrong deployment ID | Verify AGENT_DEPLOYMENT_ID matches deployed agent |
| 503 Service Unavailable | Agent not configured | Set all required runtime parameters |
| Timeout | Agent processing | Agent responses can take several minutes; be patient |
| CORS errors | Wrong endpoint | Ensure backend proxies requests correctly |

### Debugging Tips

1. **Check agent status endpoint**:
   ```bash
   curl http://localhost:8000/api/v1/agent/status
   ```

2. **Check agent status in DataRobot UI**:
   Navigate to Deployments and verify your agent is healthy

3. **View agent logs**:
   ```bash
   drapps logs "Agent Name"
   ```

4. **Test agent directly** (bypassing custom app):
   ```bash
   cd agent-templates
   task agent:cli -- execute-deployment --deployment_id <ID> --user_prompt "Test"
   ```

5. **Check custom app logs** in DataRobot Custom Applications UI

### Agent Template Issues

| Issue | Solution |
|-------|----------|
| `task` not found | Install Taskfile: https://taskfile.dev/installation/ |
| `uv` not found | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Pulumi errors | Run `pulumi login --local` or configure Pulumi cloud |
| Python errors | Ensure Python 3.11+ is installed |

---

## UI Components for Agent Applications

### Default: DataRobot UI (dr-ui)

**ALWAYS use DataRobot UI (dr-ui) as the primary component library for agent chat interfaces unless explicitly stated otherwise.**

[dr-ui](https://dr-ui.datarobot.com/) provides production-ready chat components specifically designed for AI agent applications:

```tsx
import { Chat, ChatMessage, ChatInput } from '@dr-ui/chat'
import { useChat } from '@dr-ui/hooks'

function AgentChat() {
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

### Key dr-ui Features for Agents
- **Chat Components**: `Chat`, `ChatMessage`, `ChatInput` - complete chat UI
- **useChat Hook**: Manages messages, streaming, loading states
- **DataRobot Theming**: Consistent with DataRobot platform styling
- **Accessibility**: Built on Radix UI primitives
- **Dark Mode**: Automatic theme support

### Component Priority
1. **dr-ui** - Use for all chat interfaces and common UI elements
2. **shadcn/ui** - Use only when dr-ui doesn't have the component
3. **Custom** - Build only when necessary, follow dr-ui patterns

See `UI_DESIGN.md` for comprehensive design documentation.

---

## For AI Assistants

When a user asks to create an AI agent chatbot, follow these steps:

### 1. Assess Requirements

Ask about:
- What should the agent do? (research, answer questions, automate tasks)
- What data sources should it use? (documents, APIs, databases)
- Multi-agent or single agent?
- Performance requirements?

### 2. Select Framework

Based on requirements:
- Multi-agent collaboration → **CrewAI**
- Complex state/workflows → **LangGraph**
- Document/RAG focus → **LlamaIndex**
- Performance critical → **NeMo Agent Toolkit**
- Custom needs → **Generic Base**

### 3. Create Agent

1. Navigate to `agent-templates/`
2. Run `task start` and select framework
3. Customize agents in the framework directory
4. Test locally with `task agent:cli`

### 4. Deploy Agent

1. Configure Pulumi: `pulumi login --local`
2. Deploy: `task deploy`
3. Save the Deployment ID

### 5. Connect to Custom App

1. Set AGENT_DEPLOYMENT_ID in `.env`
2. Ensure DATAROBOT_API_TOKEN is configured
3. **Use dr-ui chat components** for the interface (see "UI Components for Agent Applications" above)
4. Test the chat interface

### 6. Deploy Custom App

```bash
python scripts/deploy.py
```

Configure runtime parameters in DataRobot UI.

---

## Resources

- [DataRobot Agent Templates README](agent-templates/README.md)
- [DataRobot Documentation](https://docs.datarobot.com/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
