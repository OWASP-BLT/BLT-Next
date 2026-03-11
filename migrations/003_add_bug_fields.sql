-- Migration: Add url, type, and steps columns to bugs table
-- These fields are collected by the report-bug form but were missing from the schema.

ALTER TABLE bugs ADD COLUMN url TEXT;
ALTER TABLE bugs ADD COLUMN type TEXT;
ALTER TABLE bugs ADD COLUMN steps TEXT;

-- SQLite does not support ALTER CONSTRAINT directly.
-- Recreate bugs table to update the severity CHECK constraint to include 'info'.
ALTER TABLE bugs RENAME TO bugs_old;

CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical', 'info')),
    url TEXT,
    type TEXT,
    steps TEXT,
    status TEXT DEFAULT 'open',
    reporter_id INTEGER,
    reward_amount REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

INSERT INTO bugs SELECT id, title, description, severity, url, type, steps, status, reporter_id, reward_amount, created_at, updated_at FROM bugs_old;

DROP TABLE bugs_old;
