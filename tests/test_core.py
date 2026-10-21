
import pytest

from daymate.core import TaskManager


def test_add_and_list_tasks():
    manager = TaskManager()

    task = manager.add_task("Prepare hackathon demo")

    assert task["id"] == 1
    assert task["title"] == "Prepare hackathon demo"
    assert task["completed"] is False
    assert manager.list_tasks() == [task]


def test_complete_task():
    manager = TaskManager()
    task = manager.add_task("Write README")

    completed = manager.complete_task(task["id"])

    assert completed["completed"] is True


def test_empty_task_is_rejected():
    manager = TaskManager()

    with pytest.raises(ValueError, match="cannot be empty"):
        manager.add_task("   ")


def test_unknown_task_is_rejected():
    manager = TaskManager()

    with pytest.raises(ValueError, match="was not found"):
        manager.complete_task(999)
