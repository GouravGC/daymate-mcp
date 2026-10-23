
import asyncio
import json
import os
import re
from datetime import datetime

import requests
import streamlit as st
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

load_dotenv()

st.set_page_config(
    page_title="DayMate AI Planner",
    page_icon="📅",
    layout="wide",
)

MCP_URL = os.getenv(
    "MCP_SERVER_URL",
    "https://daymate-mcp-latest.onrender.com/mcp",
)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")


def decode_result(result):
    if getattr(result, "isError", False):
        messages = [
            getattr(item, "text", "")
            for item in getattr(result, "content", [])
        ]
        raise RuntimeError(
            "\n".join(m for m in messages if m) or "MCP tool failed."
        )

    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured

    parts = [
        item.text
        for item in getattr(result, "content", [])
        if getattr(item, "text", None)
    ]
    combined = "\n".join(parts).strip()

    if not combined:
        return None

    try:
        return json.loads(combined)
    except json.JSONDecodeError:
        return combined


async def _invoke_tool(name, arguments=None):
    async with streamablehttp_client(MCP_URL) as (reader, writer, _):
        async with ClientSession(reader, writer) as session:
            await session.initialize()

            tools = await session.list_tools()
            names = {tool.name for tool in tools.tools}

            if name not in names:
                raise RuntimeError(f"MCP tool '{name}' is unavailable.")

            result = await session.call_tool(
                name,
                arguments=arguments or {},
            )
            return decode_result(result)


def invoke_tool(name, arguments=None):
    return asyncio.run(_invoke_tool(name, arguments))


def normalize_tasks(data):
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]

    if isinstance(data, dict):
        for key in ("tasks", "result", "data"):
            if key in data:
                return normalize_tasks(data[key])

        if "id" in data and "title" in data:
            return [data]

    return []


def load_tasks():
    return normalize_tasks(invoke_tool("list_tasks"))


def generate_plan(goal, days, hours_per_day):
    import os
    import json
    import re
    import requests

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL", "openrouter/free")

    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY is missing. Configure it in your environment."
        )

    prompt = f"""
Create a practical task plan for this goal: {goal}

Duration: {days} days
Available time per day: {hours_per_day} hours

Return a JSON object with this exact structure:
{{
  "tasks": [
    {{
      "title": "Study Python variables",
      "day": 1,
      "duration_minutes": 30,
      "priority": "High"
    }}
  ]
}}

Requirements:
- Generate 3 to 10 actionable tasks.
- Each task must have a short title.
- day must be an integer from 1 to {days}.
- duration_minutes must be a positive integer.
- priority must be High, Medium, or Low.
- Return only JSON, without Markdown or explanations.
"""

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You are a task-planning assistant. "
                            "Return one valid JSON object only. "
                            "Do not use Markdown or add explanations."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.1,
                "max_tokens": 1500,
            },
            timeout=60,
        )

        if not response.ok:
            raise RuntimeError(
                f"OpenRouter error {response.status_code}: "
                f"{response.text[:400]}"
            )

        result = response.json()
        choices = result.get("choices", [])

        if not choices:
            raise ValueError(
                f"The AI returned no choices: {str(result)[:300]}"
            )

        content = choices[0].get("message", {}).get("content", "")

        if isinstance(content, list):
            content = "\n".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )

        if not isinstance(content, str) or not content.strip():
            raise ValueError("The AI returned an empty response.")

        # Remove optional Markdown fences.
        cleaned = content.strip()
        cleaned = re.sub(
            r"^\s*```(?:json)?\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\s*```\s*$", "", cleaned)

        # First, try parsing the entire response.
        data = None

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            pass

        # If the model included extra text, extract a JSON object.
        if data is None:
            decoder = json.JSONDecoder()

            for match in re.finditer(r"\{", cleaned):
                try:
                    candidate, _ = decoder.raw_decode(
                        cleaned[match.start():]
                    )

                    if isinstance(candidate, dict) and "tasks" in candidate:
                        data = candidate
                        break

                except json.JSONDecodeError:
                    continue

        if not isinstance(data, dict):
            raise ValueError(
                "Could not parse the AI response as JSON. "
                "Please try generating the plan again."
            )

        raw_tasks = data.get("tasks")

        if not isinstance(raw_tasks, list):
            raise ValueError(
                "The AI response does not contain a valid tasks list."
            )

        tasks = []

        for item in raw_tasks:
            if not isinstance(item, dict):
                continue

            title = item.get("title")

            if not isinstance(title, str) or not title.strip():
                continue

            try:
                day = int(item.get("day", 1))
                duration = int(item.get("duration_minutes", 30))
            except (TypeError, ValueError):
                continue

            priority = str(item.get("priority", "Medium")).capitalize()

            if priority not in {"High", "Medium", "Low"}:
                priority = "Medium"

            tasks.append({
                "title": title.strip(),
                "day": max(1, min(days, day)),
                "duration_minutes": max(1, duration),
                "priority": priority,
            })

        if not tasks:
            raise ValueError(
                "The AI did not return any usable tasks. Try again."
            )

        return tasks[:10]

    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not connect to OpenRouter: {exc}"
        ) from exc


def show_task(task, view="default"):
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
                if st.button("Complete", key=f"complete_{view}_{task_id}"):
                    try:
                        with st.spinner("Updating task..."):
                            invoke_tool(
                                "complete_task",
                                {"task_id": task_id},
                            )
                        st.session_state["notice"] = (
                            f"Task #{task_id} completed."
                        )
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Could not complete task: {exc}")


st.title("DayMate AI Planner")
st.caption(
    "Turn your goals into actionable tasks with AI, "
    "then manage them through MCP."
)

with st.sidebar:
    st.subheader("MCP Connection")
    st.code(MCP_URL, language=None)
    st.caption("Tasks are managed by your deployed MCP server.")

    if st.button("Refresh tasks", use_container_width=True):
        st.rerun()

if notice := st.session_state.pop("notice", None):
    st.success(notice)

# AI PLANNER
st.header("1. Plan a goal with AI")
st.write(
    "Describe what you want to accomplish. Review the generated plan "
    "before adding anything to your task list."
)

with st.container(border=True):
    goal = st.text_area(
        "What is your goal?",
        placeholder=(
            "Example: Prepare for an ML engineer interview "
            "covering Python, SQL, machine learning and projects."
        ),
        max_chars=1000,
        key="planner_goal",
    )

    col_days, col_hours = st.columns(2)

    with col_days:
        days = st.number_input(
            "Plan duration (days)",
            min_value=1,
            max_value=30,
            value=7,
        )

    with col_hours:
        hours_per_day = st.number_input(
            "Available hours per day",
            min_value=0.5,
            max_value=12.0,
            value=2.0,
            step=0.5,
        )

    if st.button("Generate AI plan", type="primary", use_container_width=True):
        if not goal.strip():
            st.warning("Describe your goal first.")
        else:
            try:
                with st.spinner("Generating your plan with OpenRouter..."):
                    plan = generate_plan(
                        goal.strip(),
                        int(days),
                        float(hours_per_day),
                    )

                st.session_state["plan_version"] = (
                    st.session_state.get("plan_version", 0) + 1
                )
                st.session_state["ai_plan"] = plan
                st.session_state["plan_goal"] = goal.strip()
                st.success(f"Generated {len(plan)} proposed tasks.")
            except Exception as exc:
                st.error(f"Could not generate the plan: {exc}")

# REVIEW AND APPROVE
plan = st.session_state.get("ai_plan", [])
version = st.session_state.get("plan_version", 0)

if plan:
    st.header("2. Review your plan")
    st.caption(
        "Edit titles or uncheck tasks you don't want. "
        "Nothing is added to your task list until you approve."
    )

    for index, item in enumerate(plan):
        select_key = f"plan_select_{version}_{index}"
        title_key = f"plan_title_{version}_{index}"

        if select_key not in st.session_state:
            st.session_state[select_key] = True

        if title_key not in st.session_state:
            st.session_state[title_key] = item["title"]

        with st.container(border=True):
            st.checkbox(
                f"Include task {index + 1}",
                key=select_key,
            )

            st.text_input(
                "Task title",
                key=title_key,
                max_chars=200,
            )

            st.caption(
                f"Suggested day: {item['day']} · "
                f"{item['duration_minutes']} minutes · "
                f"Priority: {item['priority']}"
            )

    if st.button(
        "Approve & Add selected tasks via MCP",
        type="primary",
        use_container_width=True,
    ):
        selected = []

        for index in range(len(plan)):
            title = st.session_state.get(
                f"plan_title_{version}_{index}", ""
            ).strip()
            include = st.session_state.get(
                f"plan_select_{version}_{index}", False
            )

            if include and title:
                selected.append(title[:200])

        if not selected:
            st.warning("Select at least one task with a valid title.")
        else:
            added = 0
            failures = []

            with st.spinner("Adding approved tasks through MCP..."):
                for title in selected:
                    try:
                        invoke_tool("add_task", {"title": title})
                        added += 1
                    except Exception as exc:
                        failures.append(f"{title}: {exc}")

            if added:
                st.session_state["notice"] = (
                    f"Successfully added {added} task(s) through MCP."
                )

            if failures:
                st.error(
                    f"{len(failures)} task(s) could not be added. "
                    "Check the errors before retrying to avoid duplicates."
                )
                for failure in failures:
                    st.caption(failure)

            if added == len(selected):
                st.session_state.pop("ai_plan", None)
                st.rerun()

st.divider()

# EXISTING MANUAL TASK ENTRY
with st.expander("Or add a single task manually"):
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input(
            "Task title",
            placeholder="e.g. Record my project demo",
            max_chars=200,
        )
        submitted = st.form_submit_button("Add task", use_container_width=True)

        if submitted:
            if not title.strip():
                st.warning("Enter a task title first.")
            else:
                try:
                    with st.spinner("Adding task..."):
                        invoke_tool("add_task", {"title": title.strip()})
                    st.session_state["notice"] = f"Task added: {title.strip()}"
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add task: {exc}")

# TASK DASHBOARD
st.header("3. Your tasks")

try:
    tasks = load_tasks()
    pending = [t for t in tasks if not t.get("completed", False)]
    completed = [t for t in tasks if t.get("completed", False)]

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
                show_task(task, view="pending")
        else:
            st.info("No pending tasks.")

    with tab_completed:
        if completed:
            for task in completed:
                show_task(task, view="completed")
        else:
            st.info("Completed tasks will appear here.")

    with tab_all:
        if tasks:
            for task in tasks:
                show_task(task, view="all")
        else:
            st.info("No tasks yet. Generate a plan or add your first task.")

    st.caption(f"Last loaded: {datetime.now().strftime('%H:%M:%S')}")

except Exception as exc:
    st.error("Unable to load tasks from the MCP server.")
    st.code(str(exc))
    st.info(
        "Check that the Render service is live and the /mcp endpoint is correct."
    )
