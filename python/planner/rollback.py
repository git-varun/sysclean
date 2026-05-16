"""Module docstring."""
import json
import sqlite3
import uuid
from datetime import datetime

DB_PATH = "runtime/state/sysclean.db"


def register_rollback(module, payload):
    """Function docstring."""

    rollback_id = str(uuid.uuid4())

    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        '''
        INSERT INTO rollback_registry (
            rollback_id,
            module,
            rollback_payload,
            created_at
        )
        VALUES (?, ?, ?, ?)
        ''',
        (
            rollback_id,
            module,
            json.dumps(payload),
            datetime.utcnow().isoformat()
        )
    )

    connection.commit()
    connection.close()

    return rollback_id
