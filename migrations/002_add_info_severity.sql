-- Migration: Add 'info' to severity CHECK constraint
-- Allows "Informational" severity bugs to be reported without being silently rejected.

BEGIN;

ALTER TABLE bugs RENAME TO bugs_old;

CREATE TABLE IF NOT EXISTS bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT CHECK(severity IN ('low', 'medium', 'high', 'critical', 'info')),
    status TEXT DEFAULT 'open',
    reporter_id INTEGER,
    reward_amount REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (reporter_id) REFERENCES users(id)
);

INSERT INTO bugs (id, title, description, severity, status, reporter_id, reward_amount, created_at, updated_at)
  SELECT id, title, description, severity, status, reporter_id, reward_amount, created_at, updated_at
  FROM bugs_old;

DROP TABLE bugs_old;

COMMIT;
