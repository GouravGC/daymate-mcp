
import sqlite3
import threading


class TaskManager:
    """SQLite-backed task manager shared across MCP sessions."""

    def __init__(self, db_path=":memory:"):
        self._lock = threading.Lock()
        self._connection = sqlite3.connect(
            db_path,
            check_same_thread=False,
            timeout=30,
        )
        self._connection.row_factory = sqlite3.Row

        with self._lock:
            self._connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            self._connection.commit()

    def add_task(self, title: str) -> dict:
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be empty.")

        with self._lock:
            cursor = self._connection.execute(
                "INSERT INTO tasks (title, completed) VALUES (?, 0)",
                (title,),
            )
            self._connection.commit()
            row = self._connection.execute(
                "SELECT id, title, completed FROM tasks WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()

        return self._to_dict(row)

    def list_tasks(self) -> list[dict]:
        with self._lock:
            rows = self._connection.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            ).fetchall()

        return [self._to_dict(row) for row in rows]

    def complete_task(self, task_id: int) -> dict:
        with self._lock:
            cursor = self._connection.execute(
                "UPDATE tasks SET completed = 1 WHERE id = ?",
                (task_id,),
            )
            self._connection.commit()

            if cursor.rowcount == 0:
                raise ValueError(f"Task {task_id} was not found.")

            row = self._connection.execute(
                "SELECT id, title, completed FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

        return self._to_dict(row)

    @staticmethod
    def _to_dict(row) -> dict:
        return {
            "id": row["id"],
            "title": row["title"],
            "completed": bool(row["completed"]),
        }
