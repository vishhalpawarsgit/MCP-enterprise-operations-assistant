"""Integration test: verify that the MCP client discovers server tools."""

import asyncio

from app.mcp_client import discover_tools


async def main():
    tools = await discover_tools()
    names = {tool["function"]["name"] for tool in tools}

    expected = {
        "search_customers",
        "get_customer",
        "search_employees_by_skill",
        "get_employee",
        "search_tickets",
        "search_policies",
    }

    print("Discovered tools:")
    for name in sorted(names):
        print(f"- {name}")

    missing = expected - names
    assert not missing, f"Missing tools: {sorted(missing)}"
    print("MCP tool discovery successful.")


if __name__ == "__main__":
    asyncio.run(main())
