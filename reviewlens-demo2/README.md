# ReviewLens Demo App — TaskFlow API

A minimal task-management REST API used to demonstrate **ReviewLens** live during the IBM Hackathon.

## What is this?

`taskflow-api` is a small Flask application that handles user task lists, task creation,
and task completion. It is intentionally kept simple so the diff stays readable on screen.

## Project Layout

```
reviewlens-demo2/
  taskflow-api/
    app.py              ← Flask application entry point
    auth.py             ← Session/token validation helpers
    tasks.py            ← Task creation, completion, and listing logic
    db.py               ← Thin database abstraction
    config.py           ← Application configuration
  frontend/
    tasks.js            ← Simple fetch-based task list renderer
  tests/
    test_tasks.py       ← Pytest suite for task logic
    test_auth.py        ← Pytest suite for auth helpers
  db/
    migrations/
      001_initial.sql   ← Initial schema
  CONTRIBUTING.md
  requirements.txt
```

## Running locally

```bash
cd reviewlens-demo2
pip install -r requirements.txt
python taskflow-api/app.py
```

## Running the demo

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the exact steps to run ReviewLens live.
