"""
MCP client used by the Groq agent.

The client launches the MCP server as a subprocess, initializes an MCP
session, discovers registered tools, and calls tools through the protocol.
It does not import or directly call the server's Python functions.
"""

import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_server_parameters() -> StdioServerParameters:
    """Describe how the MCP client launches the server process."""
    return StdioServerParameters(
        command=sys.executable,  # The Python interpreter inside uv's environment.
        args=["-m", "app.mcp_server"],
        cwd=str(PROJECT_ROOT),
    )


def mcp_tool_to_groq_schema(tool: Any) -> dict[str, Any]:
    """
    Convert an MCP tool definition into Groq's function-tool schema.

    The MCP server remains the source of truth for names, descriptions,
    and input schemas; we do not duplicate tool definitions in the agent.
    """
    return {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description or "",
            "parameters": tool.inputSchema,
        },
    }


def convert_mcp_result(result: Any) -> str:
    """Convert an MCP result to JSON text that can be sent back to the LLM."""
    if getattr(result, "isError", False):
        return json.dumps({"error": "The MCP tool reported an execution error."})

    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return json.dumps(structured, ensure_ascii=False, default=str)

    text_blocks = [
        block.text
        for block in getattr(result, "content", [])
        if getattr(block, "text", None) is not None
    ]
    if text_blocks:
        # FastMCP commonly serializes returned Python values as JSON text.
        return "\n".join(text_blocks)

    return json.dumps({"message": "The tool returned no content."})


async def discover_tools() -> list[dict[str, Any]]:
    """Start the server, initialize MCP, and return Groq-compatible tools."""
    async with stdio_client(get_server_parameters()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            response = await session.list_tools()
            return [mcp_tool_to_groq_schema(tool) for tool in response.tools]


async def execute_mcp_tool(tool_name: str, arguments: dict[str, Any]) -> str:
    """Invoke one named MCP tool using the standard MCP client API."""
    async with stdio_client(get_server_parameters()) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=arguments)
            return convert_mcp_result(result)
