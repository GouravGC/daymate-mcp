
import asyncio
import json
import os

import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


# --------------------------------------------------
# Configuration
# --------------------------------------------------

DEFAULT_MCP_URL = "https://daymate-mcp-latest.onrender.com/mcp"

st.set_page_config(
    page_title="DayMate MCP",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", DEFAULT_MCP_URL)

try:
    MCP_SERVER_URL = st.secrets.get("MCP_SERVER_URL", MCP_SERVER_URL)
except Exception:
    pass


# --------------------------------------------------
# MCP client
# --------------------------------------------------

def decode_result(result):
    """Convert MCP tool output into Python data."""
    if getattr(result, "isError", False):
        messages = [
            item.text for item in result.content
            if hasattr(item, "text")
        ]
        raise RuntimeError(
            "\n".join(messages) or "The MCP tool returned an error."
        )

    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured

    messages = [
        item.text for item in result.content
        if hasattr(item, "text")
    ]

    if not messages:
        return None

    text = "\n".join(messages)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


async def call_mcp_tool(tool_name, arguments=None):
    """Open an MCP session and invoke a tool."""
    async with streamablehttp_client(MCP_SERVER_URL) as streams:
        read_stream, write_stream, _ = streams

        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            available = {tool.name for tool in tools_result.tools}

            if tool_name not in available:
                raise RuntimeError(
                    f"Tool '{tool_name}' is unavailable. "
                    f"Available tools: {sorted(available)}"
                )

            result = await session.call_tool(
                tool_name,
                arguments=arguments or {},
            )
            return decode_result(result)


def invoke_tool(tool_name, arguments=None):
    """Run an asynchronous MCP call from Streamlit."""
    return asyncio.run(call_mcp_tool(tool_name, arguments))


def normalize_tasks(result):
    """Normalize MCP task results."""
    if isinstance(result, dict):
        result = result.get("tasks", [result])

    if not isinstance(result, list):
        raise RuntimeError(f"Unexpected task response: {result!r}")

    tasks = []

    for task in result:
        if isinstance(task, dict) and "id" in task:
            tasks.append(task)

    return tasks


def refresh_tasks():
    """Always reload the task list from the backend."""
    tasks = normalize_tasks(invoke_tool("list_tasks"))
    st.session_state["tasks"] = tasks
    return tasks


# --------------------------------------------------
# Styling
# --------------------------------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1150px;
    }
    .hero {
        padding: 1.8rem;
        border-radius: 18px;
        background: linear-gradient(120deg, #102a27, #204c43);
        color: #ffffff;
        margin-bottom: 1.5rem;
    }
    .hero h1 {
        font-size: 2.4rem;
        margin-bottom: 0.4rem;
    }
    .hero p {
        color: #d4e7df;
        margin-bottom: 0;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 14px;
        padding: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# Sidebar and header
# --------------------------------------------------

with st.sidebar:
    st.markdown("## 🌱 DayMate")
    st.caption("Your everyday productivity companion")
    st.divider()

    st.markdown("### Backend")
    st.code(MCP_SERVER_URL, language=None)

    if st.button("↻ Refresh tasks", use_container_width=True):
        st.session_state["force_refresh"] = True
        st.rerun()

    st.divider()
    st.caption("Powered by Python, Streamlit and MCP")

st.markdown(
    """
    <div class="hero">
        <h1>🌱 DayMate MCP</h1>
        <p>Make progress, one task at a time.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "Manage your tasks through the Model Context Protocol backend."
)


# --------------------------------------------------
# Load task data
# --------------------------------------------------

try:
    if st.session_state.pop("force_refresh", False):
        st.session_state.pop("tasks", None)

    # Always retrieve fresh data instead of trusting stale UI state.
    tasks = refresh_tasks()
    connected = True
    error_message = None

except Exception as exc:
    tasks = []
    connected = False
    error_message = repr(exc)

if not connected:
    st.error("Could not load tasks from the MCP backend.")
    st.warning(
        "The connection or task-list request failed. "
        "Check the Render service logs and MCP response."
    )
    with st.expander("Connection details", expanded=True):
        st.code(error_message or "Unknown error")
    st.stop()

st.success("Connected to the DayMate MCP backend.")


# --------------------------------------------------
# Task statistics
# --------------------------------------------------

completed_count = sum(
    bool(task.get("completed", False)) for task in tasks
)
pending_count = len(tasks) - completed_count

col1, col2, col3 = st.columns(3)
col1.metric("Total tasks", len(tasks))
col2.metric("Pending", pending_count)
col3.metric("Completed", completed_count)

st.divider()


# --------------------------------------------------
# Add task
# --------------------------------------------------

st.subheader("➕ Add a task")

with st.form("add_task_form", clear_on_submit=True):
    title = st.text_input(
        "What do you need to do?",
        placeholder="e.g. Prepare my hackathon demo",
        max_chars=200,
    )

    submitted = st.form_submit_button(
        "Add task",
        type="primary",
        use_container_width=True,
    )

    if submitted:
        if not title.strip():
            st.warning("Enter a task title first.")
        else:
            try:
                created = invoke_tool(
                    "add_task",
                    {"title": title.strip()},
                )

                # Fetch the list immediately after creating the task.
                tasks = refresh_tasks()

                st.session_state["flash_message"] = (
                    f"Task added: {created}"
                )
                st.rerun()

            except Exception as exc:
                st.error(
                    "The add or refresh operation failed. "
                    "Check the backend response."
                )
                st.code(repr(exc))

if "flash_message" in st.session_state:
    st.success(st.session_state.pop("flash_message"))


# --------------------------------------------------
# Task list
# --------------------------------------------------

st.subheader("📋 Your tasks")

if not tasks:
    st.info("No tasks yet. Add your first task above to get started.")

else:
    pending_tasks = [
        task for task in tasks
        if not task.get("completed", False)
    ]
    completed_tasks = [
        task for task in tasks
        if task.get("completed", False)
    ]

    if pending_tasks:
        st.markdown("#### In progress")

        for task in pending_tasks:
            task_id = task["id"]

            with st.container(border=True):
                col_task, col_action = st.columns(
                    [5, 1],
                    vertical_alignment="center",
                )

                col_task.markdown(
                    f"**{task.get('title', 'Untitled task')}**"
                )
                col_task.caption(f"Task ID: {task_id}")

                if col_action.button(
                    "Complete",
                    key=f"complete_{task_id}",
                    use_container_width=True,
                ):
                    try:
                        invoke_tool(
                            "complete_task",
                            {"task_id": int(task_id)},
                        )

                        # Verify the updated task list from the server.
                        tasks = refresh_tasks()

                        st.session_state["flash_message"] = (
                            f"Task #{task_id} completed."
                        )
                        st.rerun()

                    except Exception as exc:
                        st.error("Could not complete or refresh the task.")
                        st.code(repr(exc))

    if completed_tasks:
        with st.expander(
            f"✅ Completed tasks ({len(completed_tasks)})",
            expanded=True,
        ):
            for task in completed_tasks:
                st.markdown(
                    f"- ~~{task.get('title', 'Untitled task')}~~ "
                    f"`#{task['id']}`"
                )


# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()
st.caption(
    "DayMate MCP · Actions are executed by the remote MCP server. "
    "Tasks use the backend's in-memory storage."
)
