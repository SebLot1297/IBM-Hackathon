-- TaskFlow schema migration 002
-- Add labels/tags table
-- NOTE: This migration was included by mistake — it is unrelated to the
--       task completion feature described in this PR.

CREATE TABLE IF NOT EXISTS labels (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL UNIQUE,
    colour      TEXT NOT NULL DEFAULT '#cccccc'
);

CREATE TABLE IF NOT EXISTS task_labels (
    task_id     TEXT NOT NULL REFERENCES tasks(id),
    label_id    TEXT NOT NULL REFERENCES labels(id),
    PRIMARY KEY (task_id, label_id)
);

ALTER TABLE tasks ADD COLUMN priority INTEGER NOT NULL DEFAULT 0;
