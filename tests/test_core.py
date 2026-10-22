
from daymate.core import TaskManager


def test_add_and_list_task(tmp_path):
    manager = TaskManager(str(tmp_path / "tasks.db"))

    task = manager.add_task("Prepare demo")

    assert task["id"] == 1
    assert task["title"] == "Prepare demo"
    assert task["completed"] is False
    assert manager.list_tasks() == [task]


def test_complete_task(tmp_path):
    manager = TaskManager(str(tmp_path / "tasks.db"))
    task = manager.add_task("Record demo")

    completed = manager.complete_task(task["id"])

    assert completed["completed"] is True
    assert manager.list_tasks()[0]["completed"] is True


def test_tasks_survive_new_manager_instance(tmp_path):
    database = str(tmp_path / "tasks.db")
    first_manager = TaskManager(database)
    first_manager.add_task("Verify deployment")

    second_manager = TaskManager(database)

    assert len(second_manager.list_tasks()) == 1
    assert second_manager.list_tasks()[0]["title"] == "Verify deployment"


def test_empty_title_is_rejected(tmp_path):
    manager = TaskManager(str(tmp_path / "tasks.db"))

    try:
        manager.add_task("   ")
        assert False, "Expected ValueError for an empty title"
    except ValueError as exc:
        assert "empty" in str(exc).lower()


def test_missing_task_cannot_be_completed(tmp_path):
    manager = TaskManager(str(tmp_path / "tasks.db"))

    try:
        manager.complete_task(999)
        assert False, "Expected ValueError for a missing task"
    except ValueError as exc:
        assert "not found" in str(exc).lower()
