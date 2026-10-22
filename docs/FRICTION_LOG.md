# DayMate MCP — Development Friction Log

## Friction 1: Duplicate Streamlit Widget Keys

**Area:** Streamlit frontend

**Severity:** Medium

**Problem:** The same task appeared in multiple views, including Pending and All Tasks. The completion buttons reused the same widget key, causing Streamlit to raise a duplicate-element-key error.

**Steps to reproduce:**
1. Create a task.
2. Display it in both Pending and All Tasks.
3. Render completion buttons using the same key for the same task ID.

**Expected behavior:** The same task should be displayed in multiple views without crashing the application.

**Actual behavior:** Streamlit reported a duplicate widget key.

**Resolution:** Include a view identifier in each button key, such as `complete_pending_1` and `complete_all_1`.

**Suggested improvement:** Provide clearer diagnostics when widget keys collide and document best practices for reusable components displayed across multiple tabs.

**Status:** Fixed in the local frontend code; confirm the deployed version after pushing the change.

## Friction 2: Verifying a Remote MCP Endpoint

**Area:** MCP transport and developer onboarding

**Severity:** Low to Medium

**Problem:** Opening an MCP endpoint directly in a normal browser is not equivalent to testing it with an MCP client. Streamable HTTP requests may require specific headers and protocol initialization.

**Steps to reproduce:**
1. Open the deployed `/mcp` endpoint directly in a browser.
2. Observe that a normal page response may not be returned.
3. Test the endpoint using an MCP client that initializes a session and lists tools.

**Expected behavior:** Developers should have a clear way to determine whether the MCP server is healthy.

**Actual behavior:** A browser response alone can be confusing and does not prove whether MCP initialization and tool discovery work.

**Resolution:** Use the official Python MCP client to initialize a session and discover tools. The live test negotiated protocol `2025-11-25` and discovered `add_task`, `list_tasks`, and `complete_task`.

**Suggested improvement:** Add a documented health-check procedure or diagnostic command that tests protocol initialization and tool discovery.

**Status:** Live MCP connection and tool discovery verified.

## Submission Note

This log records development issues observed while building and testing DayMate MCP. It should be updated if additional reproducible friction is discovered. These entries are development observations, not claims about official AWS or Alexa+ product defects.