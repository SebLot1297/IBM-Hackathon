"""
Tests for tasks.py — task creation, completion, and listing logic.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'taskflow-api'))

import pytest
import db
import tasks


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_db():
    """Reset in-memory DB to a known state before each test."""
    db._users = {
        "user_001": {"id": "user_001", "name": "Alice Chen"},
        "user_002": {"id": "user_002", "name": "Bob Marsh"},
    }
    db._tasks = [
        {"id": "task_001", "owner_id": "user_001", "title": "Write spec", "done": False, "created_at": "2024-03-01T08:00:00Z"},
        {"id": "task_002", "owner_id": "user_002", "title": "Review PRs", "done": False, "created_at": "2024-03-01T09:00:00Z"},
    ]
    db._task_counter = 2
    yield


# ─── create_task ─────────────────────────────────────────────────────────────

def test_create_task_happy_path():
    result = tasks.create_task("user_001", "Buy groceries")
    assert result["ok"] is True
    assert result["task"]["title"] == "Buy groceries"
    assert result["task"]["owner_id"] == "user_001"
    assert result["task"]["done"] is False


def test_create_task_empty_title():
    result = tasks.create_task("user_001", "")
    assert result["ok"] is False
    assert "title" in result["error"]


def test_create_task_title_too_long():
    result = tasks.create_task("user_001", "x" * 201)
    assert result["ok"] is False
    assert "exceeds" in result["error"]


def test_create_task_unknown_user():
    result = tasks.create_task("user_999", "Some task")
    assert result["ok"] is False


def test_create_task_whitespace_title():
    result = tasks.create_task("user_001", "   ")
    assert result["ok"] is False


def test_create_task_appended_to_store():
    tasks.create_task("user_001", "New task")
    assert len(db._tasks) == 3


# ─── complete_task ────────────────────────────────────────────────────────────

def test_complete_task_happy_path():
    result = tasks.complete_task("user_001", "task_001")
    assert result["ok"] is True
    assert result["task"]["done"] is True


def test_complete_task_not_owner():
    result = tasks.complete_task("user_002", "task_001")
    assert result["ok"] is False
    assert "authorized" in result["error"]


def test_complete_task_already_done():
    tasks.complete_task("user_001", "task_001")
    result = tasks.complete_task("user_001", "task_001")
    assert result["ok"] is False
    assert "already" in result["error"]


def test_complete_task_not_found():
    result = tasks.complete_task("user_001", "task_999")
    assert result["ok"] is False


# ─── get_task_list ────────────────────────────────────────────────────────────

def test_get_task_list_returns_own_tasks():
    result = tasks.get_task_list("user_001")
    assert result["ok"] is True
    for t in result["tasks"]:
        assert t["owner_id"] == "user_001"


def test_get_task_list_unknown_user():
    result = tasks.get_task_list("user_999")
    assert result["ok"] is False


def test_get_task_list_pagination():
    # Insert 25 tasks for user_001
    for i in range(25):
        db.record_task = None  # patch not needed; use db.create_task directly
        db._tasks.append({
            "id": f"task_x{i:03d}",
            "owner_id": "user_001",
            "title": f"Task {i}",
            "done": False,
            "created_at": "2024-03-01T00:00:00Z",
        })
    # user_001 now has 26 tasks (1 original + 25 new)
    page1 = tasks.get_task_list("user_001", page=1)
    page2 = tasks.get_task_list("user_001", page=2)
    assert len(page1["tasks"]) == 20
    assert len(page2["tasks"]) == 6
