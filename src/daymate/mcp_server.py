
import os

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

from daymate.core import TaskManager

mcp = FastMCP(
    "DayMate MCP",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "daymate-mcp-latest.onrender.com",
            "daymate-mcp-latest.onrender.com:*",
        ],
    ),
)

manager = TaskManager()


@mcp.tool()
def add_task(title: str) -> dict:
    """Add a new task to the user's task list."""
    return manager.add_task(title)


@mcp.tool()
def list_tasks() -> list[dict]:
    """List all tasks and their completion status."""
    return manager.list_tasks()


@mcp.tool()
def complete_task(task_id: int) -> dict:
    """Mark a task as completed using its ID."""
    return manager.complete_task(task_id)


if __name__ == "__main__":
    mcp.settings.host = "0.0.0.0"
    mcp.settings.port = int(os.environ.get("PORT", "8000"))
    mcp.run(transport="streamable-http")
