"""Platform API client for Workoflow MCP Server."""

import os
from typing import Any

import httpx


class WorkoflowClient:
    """HTTP client for communicating with the Workoflow platform API."""

    def __init__(self, base_url: str | None = None):
        """Initialize the client.

        Args:
            base_url: Platform API base URL. Defaults to WORKOFLOW_API_URL env var.
        """
        self.base_url = (base_url or os.getenv("WORKOFLOW_API_URL", "http://localhost:8000")).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=60.0)
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def fetch_tools(
        self,
        prompt_token: str,
        tool_types: str | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch available tools from the platform.

        Args:
            prompt_token: User's personal access token (X-Prompt-Token).
            tool_types: Optional comma-separated tool type filter.

        Returns:
            List of tool definitions in OpenAI-compatible format.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        client = await self._get_client()

        headers = {
            "X-Prompt-Token": prompt_token,
            "Accept": "application/json",
        }

        params = {}
        if tool_types:
            params["tool_type"] = tool_types

        response = await client.get(
            f"{self.base_url}/api/mcp/tools",
            headers=headers,
            params=params,
        )
        response.raise_for_status()

        data = response.json()
        return data.get("tools", [])

    async def execute_tool(
        self,
        prompt_token: str,
        tool_id: str,
        parameters: dict[str, Any],
        execution_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute a tool on the platform.

        Args:
            prompt_token: User's personal access token (X-Prompt-Token).
            tool_id: The tool ID to execute (may include config ID suffix).
            parameters: Tool parameters.
            execution_id: Optional execution tracking ID.

        Returns:
            Tool execution result.

        Raises:
            httpx.HTTPStatusError: If the request fails.
        """
        client = await self._get_client()

        headers = {
            "X-Prompt-Token": prompt_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        body = {
            "tool_id": tool_id,
            "parameters": parameters,
        }
        if execution_id:
            body["execution_id"] = execution_id

        response = await client.post(
            f"{self.base_url}/api/mcp/execute",
            headers=headers,
            json=body,
        )
        response.raise_for_status()

        return response.json()


# Singleton instance for convenience
_client: WorkoflowClient | None = None


def get_client() -> WorkoflowClient:
    """Get the singleton WorkoflowClient instance."""
    global _client
    if _client is None:
        _client = WorkoflowClient()
    return _client
