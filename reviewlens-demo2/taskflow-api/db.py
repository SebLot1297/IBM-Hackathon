"""
TaskFlow API — thin in-memory database abstraction.
In production this would use SQLAlchemy + PostgreSQL.
"""

from typing import Optional


# Simulated in-memory store for demo purposes
_users: dict[str, dict] = {
    "user_001": {"id": "user_001", "name": "Alice Chen"},
    "user_002": {"id": "user_002", "name": "Bob Marsh"},
    "user_003": {"id": "user_003", "name": "Carol Diaz"},
}

_tasks: list[dict] = [
    {"id": "task_001", "owner_id": "user_001", "title": "Write project spec", "done": False, "created_at": "2024-03-01T08:00:00Z"},
    {"id": "task_002", "owner_id": "user_002", "title": "Review pull requests", "done": False, "created_at": "2024-03-01T09:00:00Z"},
    {"id": "task_003", "owner_id": "user_001", "title": "Deploy to staging", "done": True,  "created_at": "2024-03-02T10:30:00Z"},
]

_task_counter: int = 3


def get_user(user_id: str) -> Optional[dict]:
    """Return user dict for user_id, or None if not found."""
    return _users.get(user_id)


def create_task(task: dict) -> None:
    """Append a new task to the store."""
    _tasks.append(task)


def get_task(task_id: str) -> Optional[dict]:
    """Return a single task by id, or None if not found."""
    for t in _tasks:
        if t["id"] == task_id:
            return t
    return None


def update_task(task_id: str, updates: dict) -> bool:
    """Apply updates to a task. Returns False if not found."""
    for t in _tasks:
        if t["id"] == task_id:
            t.update(updates)
            return True
    return False


def get_tasks(user_id: str, page: int = 1, page_size: int = 20) -> list[dict]:
    """
    Return a paginated list of tasks owned by user_id.
    Pages are 1-indexed.
    """
    user_tasks = [t for t in _tasks if t["owner_id"] == user_id]
    # Calculate page slice
    start = page * page_size          # BUG: should be (page - 1) * page_size
    end = start + page_size
    return user_tasks[start:end]


def next_task_id() -> str:
    """Generate the next task ID."""
    global _task_counter
    _task_counter += 1
    return f"task_{_task_counter:03d}"
