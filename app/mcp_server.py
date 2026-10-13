"""
Acme Enterprise MCP Server.

The server exposes read-only capabilities for four simulated systems:
CRM, HR, ITSM, and Knowledge. JSON files stand in for enterprise databases
and APIs, so the learning focus remains on MCP rather than infrastructure.

Run as a module from the project root:
    uv run python -m app.mcp_server

The stdio transport uses stdout for protocol messages. Do not use print()
for server-side debugging; use logging to stderr if needed.
"""

import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Acme Enterprise Operations")

# Resolve data files relative to this source file, regardless of launch path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"


def load_json(filename: str) -> list[dict[str, Any]]:
    """Load one known JSON data file and return its list of records."""
    # Filenames are constants supplied by this module, never user input.
    path = DATA_DIR / filename
    with path.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError(f"{filename} must contain a JSON list.")
    return records


# ------------------------------ CRM tools ------------------------------

@mcp.tool()
def search_customers(search_term: str) -> list[dict[str, Any]]:
    """Search CRM customers by customer name, industry, or account manager."""
    term = search_term.strip().casefold()
    if not term:
        return []

    customers = load_json("customers.json")
    fields = ("customer_name", "industry", "account_manager")
    return [
        customer
        for customer in customers
        if any(term in str(customer[field]).casefold() for field in fields)
    ]


@mcp.tool()
def get_customer(customer_id: str) -> dict[str, Any]:
    """Retrieve a CRM customer by ID, for example C001."""
    for customer in load_json("customers.json"):
        if customer["customer_id"].casefold() == customer_id.strip().casefold():
            return customer
    return {"error": f"Customer '{customer_id}' was not found."}


# ------------------------------- HR tools ------------------------------

@mcp.tool()
def search_employees_by_skill(skill: str) -> list[dict[str, Any]]:
    """Find employees whose skills include a requested skill, e.g. Databricks."""
    requested = skill.strip().casefold()
    if not requested:
        return []

    employees = load_json("employees.json")
    return [
        employee
        for employee in employees
        if any(requested in item.casefold() for item in employee["skills"])
    ]


@mcp.tool()
def get_employee(employee_id: str) -> dict[str, Any]:
    """Retrieve an employee by ID, for example E101."""
    for employee in load_json("employees.json"):
        if employee["employee_id"].casefold() == employee_id.strip().casefold():
            return employee
    return {"error": f"Employee '{employee_id}' was not found."}


# ------------------------------ ITSM tools -----------------------------

@mcp.tool()
def search_tickets(
    customer_id: str = "",
    status: str = "",
    priority: str = "",
) -> list[dict[str, Any]]:
    """
    Search ITSM tickets using optional customer_id, status, and priority filters.
    Examples: status='Open'; priority='High', status='Open'; customer_id='C001'.
    """
    tickets = load_json("tickets.json")
    customer_filter = customer_id.strip().casefold()
    status_filter = status.strip().casefold()
    priority_filter = priority.strip().casefold()

    return [
        ticket
        for ticket in tickets
        if (not customer_filter or ticket["customer_id"].casefold() == customer_filter)
        and (not status_filter or ticket["status"].casefold() == status_filter)
        and (not priority_filter or ticket["priority"].casefold() == priority_filter)
    ]


# --------------------------- Knowledge tools ---------------------------

@mcp.tool()
def search_policies(search_term: str) -> list[dict[str, Any]]:
    """Search policy documents by title or content using keyword matching."""
    term = search_term.strip().casefold()
    if not term:
        return []

    policies = load_json("policies.json")
    return [
        policy
        for policy in policies
        if term in policy["title"].casefold()
        or term in policy["content"].casefold()
    ]


# ------------------------------ MCP resource ---------------------------

@mcp.resource("enterprise://overview")
def enterprise_overview() -> str:
    """
    Return a short description of the simulated enterprise environment.

    Resources expose contextual information. They are different from tools:
    tools perform an action, while resources provide information.
    """
    return (
        "Acme Corporation has four simulated systems: CRM for customers, "
        "HR for employee profiles and skills, ITSM for incidents and tickets, "
        "and Knowledge for company policies. CRM customers and ITSM tickets "
        "are linked by customer_id."
    )


if __name__ == "__main__":
    # stdio is suitable when an MCP client launches this server as a process.
    mcp.run(transport="stdio")
