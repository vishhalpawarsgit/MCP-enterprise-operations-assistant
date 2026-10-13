"""Integration test: invoke CRM search through the MCP protocol."""

import asyncio
import json

from app.mcp_client import execute_mcp_tool


async def main():
    result_text = await execute_mcp_tool(
        "search_customers",
        {"search_term": "ABC Industries"},
    )
    print(json.dumps(json.loads(result_text), indent=2, ensure_ascii=False))
    assert "ABC Industries" in result_text


if __name__ == "__main__":
    asyncio.run(main())
