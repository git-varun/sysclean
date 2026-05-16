"""Module docstring."""
import json
import sqlite3
import datetime
from telemetry.db import DB_PATH

def _get_connection():
    if not DB_PATH.exists():
        raise RuntimeError("Database not initialized")
    return sqlite3.connect(DB_PATH)

def register_rollback(operation):
    """Function docstring."""
    rollback = operation.get("rollback")
    if not rollback:
        return

    # Assuming operation has an id, module, and rollback is a dict payload
    rollback_id = f"rb_{operation.get('id', 'unknown')}_{datetime.datetime.utcnow().strftime('%s')}"
    operation_id = operation.get("id", "unknown")
    module = operation.get("module", "unknown")
    rollback_type = rollback.get("type", "generic")
    rollback_payload = json.dumps(rollback.get("payload", {}))
    created_at = datetime.datetime.utcnow().isoformat()

    with _get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO rollback_registry (
                rollback_id, operation_id, module, rollback_type, rollback_payload, created_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (rollback_id, operation_id, module, rollback_type, rollback_payload, created_at)
        )
        conn.commit()

def execute_rollback(rollback_id=None):
    """Function docstring."""
    with _get_connection() as conn:
        cursor = conn.cursor()
        if rollback_id:
            cursor.execute("SELECT rollback_id, rollback_type, rollback_payload FROM rollback_registry WHERE rollback_id = ?", (rollback_id,))  # pylint: disable=line-too-long
            rows = cursor.fetchall()
        else:
            # Execute latest if no ID given
            cursor.execute("SELECT rollback_id, rollback_type, rollback_payload FROM rollback_registry ORDER BY id DESC LIMIT 1")  # pylint: disable=line-too-long
            rows = cursor.fetchall()

        if not rows:
            print("No rollback metadata found.")
            return

        for rb_id, rb_type, rb_payload in rows:
            print(f"Executing rollback: {rb_id} of type {rb_type}")
            payload = json.loads(rb_payload)
            # Placeholder for actual restore logic based on rb_type
            print(f"Rollback payload: {payload}")
            print(f"Rollback {rb_id} completed successfully.")

            # Optionally remove from registry after successful rollback
            # cursor.execute("DELETE FROM rollback_registry WHERE rollback_id = ?", (rb_id,))

        conn.commit()
