# DayMate MCP — Hackathon Demo Script

**Target duration:** 2 minutes 30 seconds

## 0:00–0:20 — Introduction

"Hi, this is DayMate MCP, a lightweight task-management assistant built using the Model Context Protocol. It exposes task operations through a remotely hosted MCP server and provides a Streamlit interface for users."

## 0:20–0:45 — Show the application

Open the deployed Streamlit application.

Show the task dashboard and explain that users can add tasks, view pending tasks, and see completed tasks.

## 0:45–1:15 — Demonstrate task creation

Add a task such as "Prepare my project demo."

Show the task appearing in the pending list and explain that the frontend sends the operation to the MCP server.

## 1:15–1:40 — Demonstrate task completion

Click Complete on the new task.

Show the updated status and verify that the task appears as completed.

## 1:40–2:05 — Show the MCP integration

Show the successful live MCP client test.

Explain that the client negotiated protocol version `2025-11-25` and discovered the `add_task`, `list_tasks`, and `complete_task` tools.

## 2:05–2:20 — Show engineering practices

Briefly show the public GitHub repository and the automated GitHub Actions workflow.

## 2:20–2:30 — Closing

"DayMate MCP demonstrates how a simple task-management workflow can be exposed through interoperable MCP tools. Thank you for watching."

## Recording checklist

- Record the running application, not just static slides.
- Keep the narration in English.
- Show successful operations and genuine test output.
- Avoid exposing API keys, passwords, or other secrets.
- Upload the final video publicly to YouTube or Vimeo, following the hackathon rules.
- Add the public video URL to the hackathon submission.