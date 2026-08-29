-- FinPay initial schema
-- Migration 001

CREATE TABLE IF NOT EXISTS accounts (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    balance     REAL NOT NULL DEFAULT 0.0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS transactions (
    id          TEXT PRIMARY KEY,
    sender_id   TEXT NOT NULL REFERENCES accounts(id),
    recipient_id TEXT NOT NULL REFERENCES accounts(id),
    amount      REAL NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
