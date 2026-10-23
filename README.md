# 🌱 DayMate MCP

**Make progress, one task at a time.**

DayMate MCP is an AI-powered task-planning application that helps turn a personal goal into manageable tasks. Review an AI-generated plan, choose which tasks to keep, and manage your tasks through a deployed Model Context Protocol (MCP) server.

Built with Python, Streamlit, the Model Context Protocol, and OpenRouter.

## 🎥 Demo and Evidence

- **Demo video:** https://youtu.be/eplJfpuzee0
- **Screenshots and evidence:** https://github.com/GouravGC/daymate-mcp/tree/main/evidence
- **Source code:** https://github.com/GouravGC/daymate-mcp

## ✨ Features

- **AI-powered planning:** Turn a goal into a structured task plan using an OpenRouter-hosted language model.
- **Review before adding:** Review proposed tasks and select the ones you want to create.
- **MCP-powered task management:** Create, list, and complete tasks through the deployed MCP backend.
- **Task dashboard:** View pending, completed, and all tasks.
- **Robust AI response parsing:** Handles JSON responses that may contain Markdown code fences or surrounding text.
- **Automated testing:** Run project tests with pytest.
- **CI/CD:** GitHub Actions validates project changes; the deployment pipeline supports publishing and deploying the backend.

## 🧰 Tech Stack

| Component | Technology |
|---|---|
| Frontend | Streamlit |
| Backend | Python |
| AI planning | OpenRouter |
| Tool integration | Model Context Protocol (MCP) |
| Deployment | Render |
| Testing | pytest |
| Automation | GitHub Actions |

## 🏗️ Architecture

```text
User
  |
  v
Streamlit Application
  |
  +--> OpenRouter --> AI-generated task plan
  |                     |
  |                     v
  |              User reviews tasks
  |
  v
Approved task titles
  |
  v
Deployed MCP Server
  |
  +--> add_task(title)
  +--> list_tasks()
  +--> complete_task(task_id)
```

The AI planner proposes tasks, while the MCP server exposes the task-management tools. AI-suggested day, duration, and priority are planning information; the current MCP task tools store task titles rather than that additional metadata.

## 🔌 Deployed MCP Backend

**MCP endpoint:**

https://daymate-mcp-latest.onrender.com/mcp

The server uses the Streamable HTTP transport for MCP communication.

### Available MCP tools

| Tool | Purpose |
|---|---|
| `add_task(title: str)` | Create a task using its title. |
| `list_tasks()` | Retrieve the available tasks. |
| `complete_task(task_id: int)` | Mark a task as completed. |

These tools allow an MCP-compatible client to interact with the task-management functionality through the protocol.

## 🚀 Run Locally

### Prerequisites

- Python 3.11
- Git
- An OpenRouter API key for AI-powered planning

### 1. Clone the repository

```bash
git clone https://github.com/GouravGC/daymate-mcp.git
cd daymate-mcp
```

### 2. Create and activate a virtual environment

Windows Command Prompt:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```cmd
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure the AI API key

Configure your OpenRouter API key using the environment-variable or Streamlit secrets mechanism expected by the application. Keep your actual API key private and never commit credentials to GitHub.

### 5. Start the Streamlit application

```cmd
streamlit run app.py
```

Open the local URL printed in your terminal.

> The frontend requires its AI API key for AI-powered planning. The deployed MCP backend is hosted separately.

## 🧪 Run Tests

Run the automated test suite from the repository root:

```cmd
python -m pytest
```

## 🔄 CI/CD

The repository includes GitHub Actions automation for validating project changes. The backend deployment workflow supports building and publishing the application image and deploying it to Render.

Check the repository's **Actions** tab for the latest workflow results.

## 🔐 Limitations and Scope

- Task storage is temporary and should not be treated as durable storage; tasks may be lost when the backend restarts.
- The MCP task tools currently store task titles, not the AI planner's suggested day, duration, or priority.
- AI-generated plans are suggestions that users can review before creating tasks.
- The project demonstrates MCP-based task management and an Alexa+-style assistant workflow; it does not claim a native Alexa device integration.
- Do not use the current deployment for sensitive or production-critical task data.

## 🗺️ Future Improvements

- Persistent task storage
- Task deadlines, priorities, and duration metadata in the backend
- Authentication and user-specific task isolation
- Additional assistant and voice-platform integrations

## 🤝 Contributing

Contributions, bug reports, and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make and test your changes.
4. Open a pull request with a clear description.

## 📄 License

See the [`LICENSE`](LICENSE) file in this repository.

---

**Built by [GouravGC](https://github.com/GouravGC).**
