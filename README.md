
# DayMate MCP

An AI-ready everyday task assistant built with Python and the Model Context Protocol (MCP).

DayMate exposes task-management tools through a Streamable HTTP MCP server, providing a foundation for conversational assistants and future integrations.

## Features

- Create tasks with unique IDs.
- List tasks and their completion status.
- Mark tasks as completed.
- Validate empty task titles and unknown task IDs.
- Expose functionality through three MCP tools.
- Run automated tests with pytest.
- Use GitHub Actions for continuous integration.

## Tech Stack

- Python 3.11
- Model Context Protocol (MCP)
- Streamlit (planned)
- Pytest
- GitHub Actions

## Project Structure

```text
DayMate-MCP/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
├── logs/
├── src/
│   └── daymate/
│       ├── __init__.py
│       ├── core.py
│       └── mcp_server.py
├── tests/
│   └── test_core.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Setup

Create and activate a Conda environment with Python 3.11, then install dependencies:

```bash
python -m pip install -r requirements.txt
python -m pip check
```

## Run the MCP Server

From the project root:

**Windows CMD**

```cmd
set PYTHONPATH=src
python -m daymate.mcp_server
```

The local server uses Streamable HTTP at `http://127.0.0.1:8000`.

Keep the terminal running while connecting an MCP client. The MCP endpoint is `/mcp`; the root URL is not a web dashboard.

## Available MCP Tools

| Tool | Description |
|---|---|
| `add_task` | Create a task |
| `list_tasks` | List tasks |
| `complete_task` | Mark a task complete |

## Run Tests

```cmd
set PYTHONPATH=src
python -m pytest -v
```

## Continuous Integration

GitHub Actions runs the automated tests and checks dependency consistency on pushes and pull requests.

## Current Limitations

- Tasks are held in memory and are lost when the server restarts.
- Authentication and persistent storage are not implemented.
- The Streamlit interface and external assistant integrations are planned.
- A local MCP server does not, by itself, constitute an official Alexa+ integration.

## License

This project is licensed under the MIT License. See `LICENSE`.
CI/CD smoke test: GitHub Actions validates changes and publishes Docker images before deployment.
