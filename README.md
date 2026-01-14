# Workoflow MCP Server

MCP (Model Context Protocol) server that bridges local AI tools (Claude Code, Cursor, Windsurf, etc.) with the Workoflow orchestration platform.

## Features

- **Token-based authentication**: Uses your personal access token from Workoflow
- **Dynamic tool discovery**: Lists all tools available in your organization
- **Tool execution proxy**: Execute any Workoflow tool from your AI assistant
- **Caching**: TTL-based caching for tool definitions
- **OpenTelemetry tracing**: Integrated with Phoenix for observability

## Quick Start

### 1. Get Your Token

1. Log into Workoflow platform
2. Go to `/profile/`
3. Generate or copy your Personal Access Token

### 2. Configure Your AI Tool

Add to your Claude Code MCP configuration (`~/.claude.json` or via `claude mcp add`):

```json
{
  "mcpServers": {
    "workoflow": {
      "transport": "http",
      "url": "http://localhost:9006/mcp",
      "headers": {
        "X-Prompt-Token": "<your-personal-access-token>"
      }
    }
  }
}
```

### 3. Run the Server

**Local development:**
```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
cd src && fastmcp run workoflow_mcp.server:mcp --transport http --port 9006
```

**Docker:**
```bash
docker build -t workoflow-mcp .
docker run -p 9006:9000 --env-file .env workoflow-mcp
```

## Available Tools

Once connected, you have access to three tools:

### `workoflow_list_tools`
Lists all available tools from your Workoflow organization.

### `workoflow_execute`
Execute any tool by name with parameters.

```
Parameters:
- tool_name: The tool to execute (e.g., "jira_search_123")
- parameters: JSON string of tool parameters
```

### `workoflow_refresh`
Refresh the cached tool list after adding/removing integrations.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WORKOFLOW_API_URL` | Platform API base URL | `http://localhost:8000` |
| `TOOL_TYPES` | Comma-separated tool type filter | (all tools) |
| `CACHE_TTL_SECONDS` | Tool cache TTL in seconds | `600` |
| `OTEL_SERVICE_NAME` | OpenTelemetry service name | `workoflow-mcp` |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint for tracing | (disabled) |

## Architecture

```
AI Tool (Claude Code/Cursor)
    │
    │ MCP Protocol (Streamable HTTP)
    │ X-Prompt-Token header
    ▼
┌─────────────────────┐
│  Workoflow MCP      │
│  Server (FastMCP)   │
│  Port 9006          │
└─────────────────────┘
    │
    │ HTTP API
    │ X-Prompt-Token header
    ▼
┌─────────────────────┐
│  Workoflow Platform │
│  /api/mcp/tools     │
│  /api/mcp/execute   │
└─────────────────────┘
```

## Security

- **Token-based**: Each user authenticates with their personal access token
- **No stored credentials**: MCP server doesn't store any credentials
- **Per-request validation**: Token validated on every API call
- **Org-scoped**: Token determines which organization's tools you can access

## License

Proprietary - Workoflow Platform
