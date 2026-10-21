
from dataclasses import dataclass, field


@dataclass
class TaskManager:
    """Manage tasks for the DayMate assistant."""

    tasks: list[dict] = field(default_factory=list)
    next_id: int = 1

    def add_task(self, title: str) -> dict:
        """Create a task and return it."""
        title = title.strip()

        if not title:
            raise ValueError("Task title cannot be empty.")

        task = {
            "id": self.next_id,
            "title": title,
            "completed": False,
        }

        self.tasks.append(task)
        self.next_id += 1
        return task

    def list_tasks(self) -> list[dict]:
        """Return all tasks."""
        return [task.copy() for task in self.tasks]

    def complete_task(self, task_id: int) -> dict:
        """Mark a task as completed."""
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                return task.copy()

        raise ValueError(f"Task {task_id} was not found.")
