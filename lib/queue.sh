#!/usr/bin/env bash

# Use python to interact with the SQLite queue instead of a JSON file
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="python3"
QUEUE_PY="$ROOT_DIR/python/telemetry/queue.py"

show_queue() {
  if [ -f "$QUEUE_PY" ]; then
    $PYTHON_BIN -c "
import sys
import os
sys.path.insert(0, os.path.join('$ROOT_DIR', 'python'))
from telemetry.db import DB_PATH
import sqlite3

if DB_PATH.exists():
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM queue')
        rows = cursor.fetchall()
        if not rows:
            print('Queue is empty.')
        else:
            names = [description[0] for description in cursor.description]
            print(f\"{names}\")
            for row in rows:
                print(row)
    except Exception as e:
        print('Error reading queue:', e)
    finally:
        conn.close()
else:
    print('Queue database not found.')
"
  else
    echo "Queue module not found."
  fi
}
