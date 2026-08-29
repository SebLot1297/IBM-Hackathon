"""
TaskFlow API — Flask application entry point.
"""

import logging
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, jsonify, request, abort
import auth
import tasks
import db
from config import APP_VERSION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# ─── Health ──────────────────────────────────────────────────────────────────

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": APP_VERSION})


# ─── List Tasks ──────────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["GET"])
def list_tasks():
    user_id = auth.require_auth()
    page = int(request.args.get("page", 1))
    result = tasks.get_task_list(user_id, page=page)
    return jsonify(result)


# ─── Create Task ─────────────────────────────────────────────────────────────

@app.route("/api/tasks", methods=["POST"])
def create_task():
    # Parse request body
    body = request.get_json(force=True, silent=True) or {}
    title = body.get("title", "")

    if not title:
        abort(400, description="title is required")

    # Identify caller from token           ← BUG: require_auth() must come BEFORE body parsing
    user_id = auth.require_auth()

    result = tasks.create_task(user_id, title)

    if not result["ok"]:
        abort(400, description=result["error"])

    return jsonify(result), 201


# ─── Complete Task ────────────────────────────────────────────────────────────

@app.route("/api/tasks/<task_id>/complete", methods=["POST"])
def complete_task(task_id: str):
    """Mark a task as completed by the authenticated user."""
    user_id = auth.require_auth()

    result = tasks.complete_task(user_id, task_id)

    if not result["ok"]:
        abort(400, description=result["error"])

    return jsonify(result)


# ─── Task Summary ─────────────────────────────────────────────────────────────

@app.route("/api/tasks/summary", methods=["GET"])
def task_summary():
    """Return a count summary of pending vs completed tasks for the authenticated user."""
    current_user = auth.require_auth()

    usr = db.get_user(current_user)
    if usr is None:
        abort(404, description="User not found")

    # Fetch first page of tasks
    result = tasks.get_task_list(current_user, page=1)
    task_list = result.get("tasks", [])

    pending = sum(1 for t in task_list if not t["done"])
    completed = sum(1 for t in task_list if t["done"])

    return jsonify({
        "user_id": current_user,
        "pending": pending,
        "completed": completed,
        "total": pending + completed,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5001)
