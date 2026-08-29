# ReviewLens Demo App — FinPay API

A minimal payments REST API used to demonstrate **ReviewLens** live during the IBM Hackathon.

## What is this?

`finpay-api` is a small Flask application that handles user accounts, balance queries,
and fund transfers. It is intentionally kept simple so the diff stays readable on screen.

## Project Layout

```
reviewlens-demo/
  finpay-api/
    app.py              ← Flask application entry point
    auth.py             ← Session/token validation helpers
    payments.py         ← Transfer and balance logic
    db.py               ← Thin database abstraction
    config.py           ← Application configuration
  frontend/
    dashboard.js        ← Simple fetch-based dashboard renderer
  tests/
    test_payments.py    ← Pytest suite for payments logic
    test_auth.py        ← Pytest suite for auth helpers
  db/
    migrations/
      001_initial.sql   ← Initial schema
  CONTRIBUTING.md
  requirements.txt
```

## Running locally

```bash
cd reviewlens-demo
pip install -r requirements.txt
python finpay-api/app.py
```

## Running the demo

See [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for the exact steps to run ReviewLens live.
