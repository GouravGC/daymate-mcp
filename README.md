
# DayMate MCP

A lightweight task-management application built with Python, the Model Context Protocol (MCP), SQLite, and Streamlit.

## Features

- Add tasks through an MCP tool.
- List tasks and completion status.
- Mark tasks as completed.
- Use a Streamlit dashboard to manage tasks.
- Run automated backend tests with pytest.
- Build and deploy the backend using Docker and GitHub Actions.

## Architecture

```text
User
 |
 v
Streamlit frontend (frontend/app.py)
 |
 v
MCP Streamable HTTP client
 |
 v
DayMate MCP server (src/daymate/mcp_server.py)
 |
 v
TaskManager (src/daymate/core.py)
 |
 v
SQLite database
```

## MCP tools

| Tool | Purpose |
| --- | --- |
| `add_task(title)` | Create a task |
| `list_tasks()` | List tasks and statuses |
| `complete_task(task_id)` | Mark a task completed |

## Live deployment

- Backend service: https://daymate-mcp-latest.onrender.com/
- MCP endpoint: https://daymate-mcp-latest.onrender.com/mcp
- Frontend: Add your published Streamlit app URL here.

The backend root URL may not serve a browser webpage. Use an MCP-compatible client or the Streamlit frontend to test the MCP endpoint.

## Requirements

- Python 3.11
- pip
- Git
- Docker (optional for local container testing)

## Local setup

Clone the repository:

```bash
git clone https://github.com/GouravGC/daymate-mcp.git
cd daymate-mcp
```

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
```

Windows CMD:

```bat
.venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=src
python -m daymate.mcp_server
```

The backend listens on port 8000 by default.

In a second terminal, set up and launch the frontend:

```bat
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
```

Set `MCP_SERVER_URL` if the backend runs at a different address.

## Tests

From the repository root, run:

Windows CMD:

```bat
set PYTHONPATH=src
python -m pytest -q
```

## Deployment

The repository includes a Dockerfile and GitHub Actions workflow. Check the Actions tab for test and deployment status. Configure the required GitHub secrets in repository settings; never commit deployment tokens.

## Storage limitations

The default deployed database path is `/tmp/daymate_tasks.db`. This is suitable for a simple demonstration but is not guaranteed to survive container replacement or redeployment. Use a persistent disk or external database for durable production storage. A single SQLite file is not a shared database across multiple independent server instances.

## Security and limitations

- The current application is a demonstration task manager.
- It does not implement user authentication or per-user task isolation.
- Do not store confidential or sensitive information in tasks.
- Use HTTPS for remote connections.
- Keep deployment credentials out of source control.

## License

MIT License. See [LICENSE](LICENSE).
