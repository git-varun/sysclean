"""Module docstring."""
import json
import sqlite3
import uuid
from datetime import datetime

DB_PATH = "runtime/state/sysclean.db"


def enqueue(module: str, payload: dict) -> str:
    """Function docstring."""
    operation_id = str(uuid.uuid4())

    connection = sqlite3.connect(DB_PATH)

    connection.execute(
        '''
        INSERT INTO queue (
            operation_id,
            module,
            phase,
            status,
            created_at,
            payload_json
        )
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (
            operation_id,
            module,
            "queued",
            "pending",
            datetime.utcnow().isoformat(),
            json.dumps(payload)
        )
    )

    connection.commit()
    connection.close()

    return operation_id
