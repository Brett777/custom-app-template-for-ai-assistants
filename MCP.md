# DataRobot MCP Server Integration Guide

This document provides comprehensive guidance for AI assistants and developers working with DataRobot MCP (Model Context Protocol) Servers in Custom Applications.

## Table of Contents
1. [Overview](#overview)
2. [What is MCP?](#what-is-mcp)
3. [MCP Server Architecture](#mcp-server-architecture)
4. [Creating an MCP Server](#creating-an-mcp-server)
5. [Developing Custom Tools](#developing-custom-tools)
6. [Deploying the MCP Server](#deploying-the-mcp-server)
7. [Connecting Agents to MCP Servers](#connecting-agents-to-mcp-servers)
8. [Integration with Custom Apps](#integration-with-custom-apps)
9. [Configuration Reference](#configuration-reference)
10. [Troubleshooting](#troubleshooting)

---

## Overview

DataRobot MCP Servers enable AI agents to access external tools, data sources, and APIs through a standardized protocol. When combined with Agent Deployments and Custom Apps, you can build powerful AI applications with rich capabilities.

### Architecture: Agent + MCP + Custom App

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Custom App    │────▶│  Agent          │────▶│  MCP Server     │
│   (React UI)    │     │  Deployment     │     │  (Tools)        │
└─────────────────┘     └─────────────────┘     └─────────────────┘
   User Interface        AI Agent with          Weather, Stocks,
   Chat Component        Tool Calling           News, Custom APIs
```

**Use Cases:**
- Chatbot with real-time data access (weather, stocks, news)
- Agent that can query databases and APIs
- AI assistant with custom business logic tools
- Multi-modal applications with specialized capabilities

---

## What is MCP?

**Model Context Protocol (MCP)** is an open protocol that enables AI models to access external tools, resources, and prompts in a standardized way.

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Tools** | Functions that agents can call (e.g., `get_weather`, `search_database`) |
| **Resources** | Static data or context provided to agents |
| **Prompts** | Reusable prompt templates for common tasks |

### Why Use MCP?

- **Standardized Interface**: One protocol for all tool integrations
- **Secure**: Tools run on your infrastructure with your credentials
- **Extensible**: Easy to add custom tools and capabilities
- **Observable**: Built-in tracing with OpenTelemetry

---

## MCP Server Architecture

The MCP server template follows a modular structure:

```
mcp-server-template/
├── dr_mcp/                    # Main application code
│   ├── app/
│   │   ├── core/              # Server configuration and lifecycle
│   │   │   ├── server_lifecycle.py
│   │   │   ├── user_config.py
│   │   │   └── user_credentials.py
│   │   ├── tools/             # Tool implementations
│   │   │   └── user_tools.py  # Your custom tools
│   │   ├── prompts/           # Prompt templates
│   │   ├── resources/         # Static resources
│   │   └── main.py            # Application entry point
│   ├── pyproject.toml         # Python dependencies
│   ├── Taskfile.yaml          # Development tasks
│   ├── start-app.sh           # Startup script
│   ├── metadata.yaml          # Runtime parameters
│   └── user-metadata.yaml     # User-specific metadata
├── docs/                      # Documentation
├── infra/                     # Pulumi infrastructure
│   ├── docker/                # Docker configuration
│   └── infra/                 # Deployment definitions
├── Taskfile.yaml              # Top-level tasks
└── README.md
```

---

## Creating an MCP Server

### Prerequisites

**Required:**
- Python 3.11+
- Taskfile.dev (task runner)
- uv (Python package manager)
- Pulumi (infrastructure as code)

**Install on Windows (PowerShell):**
```powershell
# Install Taskfile
winget install Task.Task

# Install uv
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Install Pulumi
winget install Pulumi.Pulumi
```

**Install on macOS/Linux:**
```bash
# macOS
brew install go-task/tap/go-task
brew install uv
brew install pulumi

# Linux
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://get.pulumi.com | sh
```

### Step 1: Set Up Environment

```bash
# Navigate to MCP template
cd mcp-server-template

# Copy environment template
cp .env.sample dr_mcp/.env

# Edit dr_mcp/.env with your DataRobot credentials
```

**Required environment variables:**
```bash
# DataRobot credentials
DATAROBOT_API_TOKEN=your-api-token
DATAROBOT_ENDPOINT=https://app.datarobot.com

# Session security (generate with Python)
SESSION_SECRET_KEY=your-secret-key
```

Generate session secret key:
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 2: Install Dependencies

```bash
task install
```

### Step 3: Run Locally

```bash
cd dr_mcp
task dev
```

Server starts at `http://localhost:8080` with MCP endpoint at `http://localhost:8080/mcp/`

### Step 4: Test Interactively

```bash
task mcp:test-interactive
```

This opens an interactive chat to test your tools with an AI agent.

---

## Developing Custom Tools

### Basic Tool Structure

Create tools in `dr_mcp/app/tools/`:

```python
# dr_mcp/app/tools/my_tools.py
import logging
from base import dr_mcp_tool

logger = logging.getLogger(__name__)

@dr_mcp_tool(tags={"custom", "example"})
async def my_custom_tool(input_param: str, optional_param: int = 10) -> str:
    """
    Brief description of what your tool does.

    This description helps LLMs understand when and how to use your tool.
    Be specific about the tool's purpose and behavior.

    Args:
        input_param: Description of the required parameter
        optional_param: Description of the optional parameter (default: 10)

    Returns:
        Description of what the tool returns
    """
    # Your custom logic here
    result = f"Processed {input_param} with {optional_param}"
    logger.info(f"Tool executed: {result}")
    return result
```

### Tool Best Practices

| Practice | Description |
|----------|-------------|
| **Clear Descriptions** | LLMs use docstrings to understand tool capabilities |
| **Type Hints** | Always use type hints for parameters and return values |
| **Error Handling** | Return meaningful error messages in JSON format |
| **Async/Await** | Tools should be async functions for better performance |
| **Tags** | Use descriptive tags to categorize tools |
| **Logging** | Log tool execution for debugging |

### Example: Weather Tool

```python
@dr_mcp_tool(tags={"weather"})
async def current_weather(city: str) -> str:
    """
    Get current weather for a city.

    Args:
        city: Name of the city (e.g., "New York", "London")

    Returns:
        JSON string with temperature, humidity, and conditions
    """
    import httpx
    import json

    # Call weather API
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": 40.7128,  # Would use geocoding
                "longitude": -74.0060,
                "current": "temperature_2m,relative_humidity_2m"
            }
        )
        data = response.json()

    return json.dumps({
        "city": city,
        "temperature": data["current"]["temperature_2m"],
        "humidity": data["current"]["relative_humidity_2m"]
    })
```

### Adding Resources

Resources provide static data to agents:

```python
# dr_mcp/app/resources/my_resource.py
from base import dr_mcp_resource

@dr_mcp_resource(uri="custom://company-info")
async def company_info() -> str:
    """Provide company information to the agent."""
    return """
    # Company Information

    - Name: Acme Corp
    - Industry: Technology
    - Founded: 2010

    ## Products
    - Product A: Description
    - Product B: Description
    """
```

### Adding Prompts

Prompt templates for common tasks:

```python
# dr_mcp/app/prompts/my_prompt.py
from base import dr_mcp_prompt

@dr_mcp_prompt()
async def analysis_prompt(topic: str) -> str:
    """Prompt template for data analysis tasks."""
    return f"""
    You are a data analyst helping with {topic}.

    Guidelines:
    1. Use available tools to gather data
    2. Provide clear, actionable insights
    3. Include relevant visualizations when possible
    """
```

---

## Deploying the MCP Server

### Step 1: Configure Pulumi

```bash
# Login to Pulumi (local state)
pulumi login --local

# Or use Pulumi Cloud
pulumi login
```

### Step 2: Copy Environment File

```bash
# Copy .env to repository root for deployment
cp dr_mcp/.env .env
```

### Step 3: Deploy

```bash
task deploy
```

**Resources Created:**
- Docker-based Python 3.12 execution environment
- Custom model (MCP server type)
- Registered model with versioning
- Serverless prediction environment
- Active deployment with endpoint URL

### Step 4: Get Deployment Info

```bash
task infra:info
```

Save the `MCP_SERVER_MCP_ENDPOINT` URL - you'll need it to connect agents.

### Step 5: Remove Deployment (when needed)

```bash
task destroy
```

---

## Connecting Agents to MCP Servers

Once your MCP server is deployed, you can connect it to AI agents.

### Option 1: DataRobot Agent with MCP Tools

When creating an agent in DataRobot, you can configure it to use tools from your MCP server.

### Option 2: Claude Desktop / Cursor / VSCode

Configure your IDE to use the MCP server:

**Claude Desktop (`claude_desktop_config.json`):**
```json
{
  "mcpServers": {
    "datarobot-mcp": {
      "url": "https://your-mcp-endpoint.datarobot.com/mcp/"
    }
  }
}
```

**Cursor (`.cursor/mcp.json`):**
```json
{
  "mcpServers": {
    "datarobot-mcp": {
      "url": "https://your-mcp-endpoint.datarobot.com/mcp/"
    }
  }
}
```

---

## Integration with Custom Apps

### Pattern: Custom App + Agent + MCP Server

For a complete AI application:

1. **MCP Server**: Provides tools (weather, stocks, database queries, etc.)
2. **Agent Deployment**: AI agent configured to use MCP tools
3. **Custom App**: React UI that calls the agent

### Configuration Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                        Custom App                                │
│  ┌─────────────────┐                                            │
│  │   ChatBot.tsx   │──────▶ /api/v1/agent/chat                  │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Agent Deployment                              │
│  - Configured with MCP server URL                               │
│  - Has access to MCP tools                                      │
│  - Processes user queries                                       │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       MCP Server                                 │
│  - current_weather(city)                                        │
│  - stock_price(symbol)                                          │
│  - news_headlines(topic)                                        │
│  - custom_tool(...)                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Example: Building a Full Stack AI App

1. **Create and deploy MCP server** with your tools
2. **Create an agent** that uses the MCP server
3. **Deploy the agent** and get deployment ID
4. **Configure Custom App** with the agent deployment ID
5. **Deploy Custom App** to DataRobot

---

## Configuration Reference

### Environment Variables

**DataRobot Credentials:**
| Variable | Description | Required |
|----------|-------------|----------|
| `DATAROBOT_API_TOKEN` | DataRobot API token | Yes |
| `DATAROBOT_ENDPOINT` | DataRobot instance URL | Yes |
| `SESSION_SECRET_KEY` | Session encryption key | Yes |

**MCP Server Configuration:**
| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_NAME` | Server display name | `datarobot-mcp-server` |
| `MCP_SERVER_PORT` | Server port | `8080` |
| `MCP_SERVER_HOST` | Server host | `0.0.0.0` |
| `MCP_SERVER_LOG_LEVEL` | MCP log level | `WARNING` |
| `APP_LOG_LEVEL` | Application log level | `INFO` |

**Advanced Configuration:**
| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_SERVER_REGISTER_DYNAMIC_TOOLS_ON_STARTUP` | Auto-register tools | `false` |
| `OTEL_ENABLED` | Enable OpenTelemetry tracing | `true` |
| `ENABLE_PREDICTIVE_TOOLS` | Enable prediction tools | `false` |

### Runtime Parameters (metadata.yaml)

```yaml
runtimeParameterDefinitions:
  - fieldName: mcp_server_name
    type: string
  - fieldName: mcp_server_log_level
    type: string
  - fieldName: app_log_level
    type: string
  - fieldName: otel_enabled
    type: boolean
  - fieldName: enable_predictive_tools
    type: boolean
```

---

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `task` not found | Taskfile not installed | Install Taskfile.dev |
| `uv` not found | uv not installed | Install uv package manager |
| Server won't start | Missing credentials | Check DATAROBOT_API_TOKEN and DATAROBOT_ENDPOINT |
| Tools not appearing | Registration error | Check tool docstrings and type hints |
| Connection refused | Port in use | Change MCP_SERVER_PORT |
| 401 Unauthorized | Invalid token | Verify API token is correct |

### Debugging Tips

1. **Check server logs:**
   ```bash
   # Local development
   cd dr_mcp && task dev  # Watch console output

   # Deployed server
   task infra:info  # Get deployment info
   ```

2. **Test tools interactively:**
   ```bash
   task mcp:test-interactive
   ```

3. **Verify tool registration:**
   - Tools must have docstrings
   - Parameters must have type hints
   - Function must be async

4. **Check MCP endpoint:**
   ```bash
   curl http://localhost:8080/mcp/
   ```

### Log Locations

| Client | Log Location |
|--------|-------------|
| Local | Console output |
| Cursor | Output panel → "MCP Logs" |
| Claude Desktop | `~/Library/Logs/Claude/mcp*.log` |
| VSCode | Output panel → Select MCP server |

---

## For AI Assistants

When a user asks to create an MCP server or add tools to an agent:

### Step 1: Determine Requirements

Ask about:
- What tools/capabilities do they need?
- What APIs or data sources to integrate?
- Will this connect to an existing agent?

### Step 2: Create MCP Server

1. Navigate to `mcp-server-template/`
2. Create tools in `dr_mcp/app/tools/`
3. Test locally with `task dev`
4. Test interactively with `task mcp:test-interactive`

### Step 3: Deploy MCP Server

```bash
cd mcp-server-template
pulumi login --local
cp dr_mcp/.env .env
task deploy
```

Save the MCP endpoint URL.

### Step 4: Connect to Agent

Configure the agent deployment to use the MCP server URL.

### Step 5: Integrate with Custom App

If building a full application, use the Custom App template with:
- Agent deployment ID configured
- ChatBot component for user interaction

---

## Resources

- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [DataRobot MCP Template README](mcp-server-template/README.md)
- [FastMCP Documentation](https://github.com/jlowin/fastmcp)
- [DataRobot Documentation](https://docs.datarobot.com/)
