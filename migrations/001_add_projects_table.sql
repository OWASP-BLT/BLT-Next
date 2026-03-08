-- Migration: Add projects table
-- This migration adds the projects table that was missing from the initial schema.
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT,
    reward TEXT DEFAULT 'N/A',
    bugs INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
