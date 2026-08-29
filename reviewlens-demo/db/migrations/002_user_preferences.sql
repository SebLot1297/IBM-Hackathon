-- FinPay schema migration 002
-- Add user preferences table
-- NOTE: This migration was included by mistake — it is unrelated to the
--       user dashboard feature described in this PR.

CREATE TABLE IF NOT EXISTS user_preferences (
    user_id         TEXT PRIMARY KEY REFERENCES accounts(id),
    currency        TEXT NOT NULL DEFAULT 'USD',
    notifications   INTEGER NOT NULL DEFAULT 1,
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

ALTER TABLE transactions ADD COLUMN note TEXT;
