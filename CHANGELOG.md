# Changelog

All notable changes to this project will be documented in this file.

## 2026-01-14

### Added
- **Initial release** - MCP Server Bridge for Workoflow Platform
- **Token-based authentication** - Uses personal access tokens from Workoflow profile (`X-Prompt-Token` header)
- **Tool discovery** - `workoflow_list_tools` command to list all available tools from your organization
- **Tool execution** - `workoflow_execute` command to run any Workoflow tool by name with parameters
- **Cache refresh** - `workoflow_refresh` command to refresh the cached tool list
- **TTL caching** - Configurable cache for tool definitions (default 10 minutes)
- **OpenTelemetry integration** - Phoenix tracing support for observability
- **Docker support** - Dockerfile and docker-compose integration for workoflow-ai-setup
- **Streamable HTTP transport** - Modern MCP transport protocol for Claude Code, Cursor, and other AI tools
