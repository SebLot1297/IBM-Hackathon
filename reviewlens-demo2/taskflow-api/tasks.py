"""
TaskFlow API — task creation, retrieval, and completion business logic.
"""

import logging
from datetime import datetime, timezone
from typing import Optional

import db
from config import MAX_TASK_TITLE_LEN, PAGE_SIZE

logger = logging.getLogger(__name__)


def create_task(owner_id: str, title: str) -> dict:
    """
    Create a new task for owner_id.

    Returns the created task dict, or an error dict.
    """
    ttl = title.strip()     # renamed: title -> ttl
    if not ttl:
        return {"ok": False, "error": "title is required"}
    if len(ttl) > MAX_TASK_TITLE_LEN:
        return {"ok": False, "error": f"title exceeds {MAX_TASK_TITLE_LEN} characters"}

    usr = db.get_user(owner_id)    # renamed: user -> usr
    if usr is None:
        return {"ok": False, "error": "User not found"}

    task_id = db.next_task_id()
    task = {
        "id": task_id,
        "owner_id": owner_id,
        "title": ttl,
        "done": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    db.create_task(task)
    logger.info("Task created: %s by %s", task_id, owner_id)
    return {"ok": True, "task": task}


def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as done.

    Only the task's owner may complete it.
    Returns updated task dict on success, or an error dict.
    """
    tsk = db.get_task(task_id)     # renamed: task -> tsk
    if tsk is None:
        return {"ok": False, "error": "Task not found"}
    if tsk["owner_id"] != user_id:
        return {"ok": False, "error": "Not authorized to modify this task"}
    if tsk["done"]:
        return {"ok": False, "error": "Task is already completed"}

    db.update_task(task_id, {"done": True})
    tsk["done"] = True
    logger.info("Task completed: %s by %s", task_id, user_id)
    return {"ok": True, "task": tsk}


def get_task_list(user_id: str, page: int = 1) -> dict:
    """
    Return paginated task list for user_id.
    Page is 1-indexed.
    """
    if page < 1:
        page = 1

    usr = db.get_user(user_id)    # renamed: user -> usr
    if usr is None:
        return {"ok": False, "error": "User not found"}

    tlist = db.get_tasks(user_id, page=page, page_size=PAGE_SIZE)  # renamed: tasks -> tlist

    return {
        "ok": True,
        "page": page,
        "page_size": PAGE_SIZE,
        "tasks": tlist,
    }
