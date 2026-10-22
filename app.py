
import asyncio
import json
import os
from datetime import datetime

import streamlit as st
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client


st.set_page_config(
    page_title="DayMate MCP",
    page_icon="📅",
    layout="wide",
)

MCP_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://daymate-mcp-latest.onrender.com/mcp",
)


def decode_result(result):
    if getattr(result, "isError", False):
        messages = [
            getattr(item, "text", "")
            for item in getattr(result, "content", [])
        ]
        raise RuntimeError("\n".join(m for m in messages if m) or "MCP tool failed.")

    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured

    parts = []
    for item in getattr(result, "content", []):
        text = getattr(item, "text", None)
        if text:
            parts.append(text)

    combined = "\n".join(parts).strip()
    if not combined:
        return None

    try:
        return json.loads(combined)
    except json.JSONDecodeError:
        return combined


async def _invoke_tool(name, arguments=None):
    async with streamablehttp_client(MCP_URL) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            available = await session.list_tools()
            names = {tool.name for tool in available.tools}
            if name not in names:
                raise RuntimeError(
                    f"Tool '{name}' is unavailable. Found: {', '.join(sorted(names))}"
                )

            result = await session.call_tool(name, arguments=arguments or {})
            return decode_result(result)


def invoke_tool(name, arguments=None):
    return asyncio.run(_invoke_tool(name, arguments))


def normalize_tasks(data):
    if isinstance(data, list):
        return [task for task in data if isinstance(task, dict)]

    if isinstance(data, dict):
        for key in ("tasks", "result", "data"):
            if key in data:
                return normalize_tasks(data[key])

        if "id" in data and "title" in data:
            return [data]

    return []


def load_tasks():
    return normalize_tasks(invoke_tool("list_tasks"))


def show_task(task):
    task_id = task.get("id", "?")
    title = str(task.get("title", "Untitled task"))
    completed = bool(task.get("completed", False))

    with st.container(border=True):
        left, right = st.columns([5, 1])
        with left:
            if completed:
                st.markdown(f"~~{title}~~")
                st.caption(f"Task #{task_id} · Completed")
            else:
                st.markdown(f"**{title}**")
                st.caption(f"Task #{task_id} · Pending")

        with right:
            if not completed and isinstance(task_id, int):
                if st.button("Complete", key=f"complete_{task_id}"):
                    try:
                        with st.spinner("Updating task..."):
                            invoke_tool("complete_task", {"task_id": task_id})
                        st.session_state["notice"] = f"Task #{task_id} completed."
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not complete task: {exc}")


st.title("📅 DayMate MCP")
st.caption("Your lightweight task manager, powered by the Model Context Protocol.")
st.caption(f"Backend: {MCP_URL}")

if notice := st.session_state.pop("notice", None):
    st.success(notice)

with st.sidebar:
    st.subheader("Connection")
    st.code(MCP_URL, language=None)
    st.caption("Tasks are managed by the deployed MCP server.")
    if st.button("Refresh tasks", use_container_width=True):
        st.rerun()

st.subheader("Add a task")
with st.form("add_task_form", clear_on_submit=True):
    title = st.text_input(
        "Task title",
        placeholder="e.g. Prepare my hackathon demo",
        max_chars=200,
    )
    submitted = st.form_submit_button("＋ Add task", use_container_width=True)

    if submitted:
        if not title.strip():
            st.warning("Enter a task title first.")
        else:
            try:
                with st.spinner("Adding task..."):
                    created = invoke_tool("add_task", {"title": title.strip()})
                st.session_state["notice"] = f"Task added: {title.strip()}"
                st.rerun()
            except Exception as exc:
                st.error(f"Could not add task: {exc}")

st.divider()
st.subheader("Your tasks")

try:
    tasks = load_tasks()
    pending = [task for task in tasks if not task.get("completed", False)]
    completed = [task for task in tasks if task.get("completed", False)]

    col1, col2, col3 = st.columns(3)
    col1.metric("Total tasks", len(tasks))
    col2.metric("Pending", len(pending))
    col3.metric("Completed", len(completed))

    tab_pending, tab_completed, tab_all = st.tabs(
        ["Pending", "Completed", "All tasks"]
    )

    with tab_pending:
        if pending:
            for task in pending:
                show_task(task)
        else:
            st.info("No pending tasks. Add one above!")

    with tab_completed:
        if completed:
            for task in completed:
                show_task(task)
        else:
            st.info("Completed tasks will appear here.")

    with tab_all:
        if tasks:
            for task in tasks:
                show_task(task)
        else:
            st.info("No tasks yet. Create your first task above.")

    st.caption(f"Last loaded: {datetime.now().strftime('%H:%M:%S')}")
except Exception as exc:
    st.error("Unable to load tasks from the MCP server.")
    st.code(str(exc))
    st.info(
        "Check that the Render service is live, the /mcp endpoint is correct, "
        "and the latest deployment has finished."
    )
