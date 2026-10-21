
import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


async def main():
    async with streamablehttp_client(
        "http://127.0.0.1:8000/mcp"
    ) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.list_tools()
            tool_names = [tool.name for tool in result.tools]

            print("MCP connection successful!")
            print("Available tools:", tool_names)

            assert "add_task" in tool_names
            assert "list_tasks" in tool_names
            assert "complete_task" in tool_names

            added = await session.call_tool(
                "add_task",
                {"title": "Prepare Amazon hackathon demo"},
            )
            print("Add-task response:", added.content)

            listed = await session.call_tool("list_tasks", {})
            print("List-task response:", listed.content)

            print("All MCP checks passed!")


if __name__ == "__main__":
    asyncio.run(main())
