"""Dynamic tool registration for Workoflow MCP Server."""

import json
from typing import Any

from fastmcp import FastMCP
from fastmcp.tools import Tool

from .client import get_client


def convert_json_schema_to_pydantic_fields(schema: dict[str, Any]) -> dict[str, tuple[type, Any]]:
    """Convert JSON Schema properties to simple Python type hints.

    This is a simplified conversion - FastMCP will handle the actual validation.
    """
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields = {}

    type_map = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }

    for name, prop in properties.items():
        json_type = prop.get("type", "string")
        python_type = type_map.get(json_type, str)

        # Use None as default for optional fields
        default = ... if name in required else None
        fields[name] = (python_type, default)

    return fields


def create_tool_function(tool_def: dict[str, Any], prompt_token: str):
    """Create a callable function for a platform tool.

    Args:
        tool_def: OpenAI-compatible tool definition from platform.
        prompt_token: User's token for API calls.

    Returns:
        An async function that executes the tool.
    """
    func_def = tool_def.get("function", tool_def)
    tool_name = func_def["name"]
    tool_description = func_def.get("description", f"Execute {tool_name}")
    parameters_schema = func_def.get("parameters", {})

    async def tool_executor(**kwargs) -> str:
        """Execute the tool on the Workoflow platform."""
        client = get_client()

        try:
            result = await client.execute_tool(
                prompt_token=prompt_token,
                tool_id=tool_name,
                parameters=kwargs,
            )

            if result.get("success"):
                return json.dumps(result.get("result", {}), indent=2, default=str)
            else:
                error_msg = result.get("message", result.get("error", "Unknown error"))
                hint = result.get("hint", "")
                return json.dumps({
                    "error": error_msg,
                    "hint": hint,
                }, indent=2)
        except Exception as e:
            return json.dumps({
                "error": str(e),
                "hint": "Check if the platform is reachable and your token is valid.",
            }, indent=2)

    # Set function metadata
    tool_executor.__name__ = tool_name
    tool_executor.__doc__ = tool_description

    # Store schema for later use
    tool_executor._parameters_schema = parameters_schema

    return tool_executor


async def register_platform_tools(
    mcp: FastMCP,
    tools: list[dict[str, Any]],
    prompt_token: str,
) -> list[str]:
    """Register platform tools with the MCP server.

    Args:
        mcp: FastMCP server instance.
        tools: List of tool definitions from platform.
        prompt_token: User's token for API calls.

    Returns:
        List of registered tool names.
    """
    registered_names = []

    for tool_def in tools:
        func_def = tool_def.get("function", tool_def)
        tool_name = func_def.get("name")

        if not tool_name:
            continue

        # Create the tool function
        tool_fn = create_tool_function(tool_def, prompt_token)

        # Get description
        description = func_def.get("description", f"Execute {tool_name} on Workoflow platform")

        # Register with FastMCP
        try:
            mcp.add_tool_from_fn(
                fn=tool_fn,
                name=tool_name,
                description=description,
            )
            registered_names.append(tool_name)
        except Exception as e:
            # Tool might already be registered, skip
            print(f"Warning: Could not register tool {tool_name}: {e}")

    return registered_names


def unregister_all_platform_tools(mcp: FastMCP, tool_names: list[str]) -> None:
    """Unregister all platform tools from the MCP server.

    Args:
        mcp: FastMCP server instance.
        tool_names: List of tool names to unregister.
    """
    for name in tool_names:
        try:
            mcp.remove_tool(name)
        except Exception:
            pass  # Tool might not exist
