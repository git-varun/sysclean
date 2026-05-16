#!/usr/bin/env python3
"""Module docstring."""

import pathlib
import sqlite3

DB_PATH = pathlib.Path.home() / ".local/share/sysclean/telemetry.db"
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(DB_PATH)

cursor = connection.cursor()

cursor.executescript(
    """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        mode TEXT,
        reclaimed_space_mb REAL
    );

    CREATE TABLE IF NOT EXISTS queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT UNIQUE,
    module TEXT,
    phase TEXT,
    status TEXT,
    risk_level TEXT,
    created_at TEXT,
    updated_at TEXT,
    payload_json TEXT,
    rollback_json TEXT
);

CREATE TABLE IF NOT EXISTS execution_journal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_id TEXT,
    module TEXT,
    command TEXT,
    status TEXT,
    duration_ms INTEGER,
    reclaimed_bytes INTEGER,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS rollback_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rollback_id TEXT UNIQUE,
    operation_id TEXT,
    module TEXT,
    rollback_type TEXT,
    rollback_payload TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS telemetry_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_name TEXT,
    metric_value REAL,
    tags_json TEXT,
    created_at TEXT
);
    """
)

connection.commit()
connection.close()

print(f"Telemetry DB initialized at {DB_PATH}")
