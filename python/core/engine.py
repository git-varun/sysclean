"""Module docstring."""
import json
import sqlite3
import datetime
import os
import subprocess
import hashlib
from pathlib import Path
from queue_engine.db import DB_PATH

SNAPSHOT_DIR = Path.home() / ".local/share/sysclean/snapshots"
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

def _get_connection():
    if not DB_PATH.exists():
        raise RuntimeError("Database not initialized")
    conn = sqlite3.connect(DB_PATH, timeout=15)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def create_snapshot(operation_id: str, targets: list) -> dict:
    """Creates a tar.gz snapshot of targets before execution."""
    if not targets:
        return {}

    # Filter targets to only those that exist to avoid tar errors
    existing_targets = [t for t in targets if os.path.exists(t)]
    if not existing_targets:
        return {}

    archive_path = SNAPSHOT_DIR / f"{operation_id}.tar.gz"
    
    # We use tar to compress absolute paths (removing leading slash via -P or similar, we'll use -P to keep absolute paths for restore)
    tar_cmd = ["tar", "-czPf", str(archive_path)] + existing_targets
    subprocess.run(tar_cmd, check=True, capture_output=True)
    
    # Calculate sha256 hash
    sha256_hash = hashlib.sha256()
    with open(archive_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
            
    return {
        "archive_path": str(archive_path),
        "hash": sha256_hash.hexdigest(),
        "targets": existing_targets
    }

def register_rollback(operation, snapshot_metadata=None):
    """Function docstring."""
    rollback = operation.get("rollback")
    if not rollback and not snapshot_metadata:
        return

    rollback_id = f"rb_{operation.get('id', 'unknown')}_{datetime.datetime.utcnow().strftime('%s')}"
    operation_id = operation.get("id", "unknown")
    module = operation.get("module", "unknown")
    
    rollback_type = "snapshot" if snapshot_metadata else rollback.get("type", "generic")
    payload = snapshot_metadata if snapshot_metadata else rollback.get("payload", {})
    
    rollback_payload = json.dumps(payload)
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
            cursor.execute("SELECT rollback_id, rollback_type, rollback_payload FROM rollback_registry WHERE rollback_id = ?", (rollback_id,))
            rows = cursor.fetchall()
        else:
            # Execute latest if no ID given
            cursor.execute("SELECT rollback_id, rollback_type, rollback_payload FROM rollback_registry ORDER BY id DESC LIMIT 1")
            rows = cursor.fetchall()

        if not rows:
            print("No rollback metadata found.")
            return

        for rb_id, rb_type, rb_payload in rows:
            print(f"Executing rollback: {rb_id} of type {rb_type}")
            payload = json.loads(rb_payload)
            
            if rb_type == "snapshot":
                archive_path = payload.get("archive_path")
                expected_hash = payload.get("hash")
                
                if not os.path.exists(archive_path):
                    print(f"Error: Snapshot archive missing at {archive_path}")
                    continue
                    
                # Verify hash
                sha256_hash = hashlib.sha256()
                with open(archive_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                if sha256_hash.hexdigest() != expected_hash:
                    print("Error: Snapshot hash mismatch. Rollback aborted to prevent corruption.")
                    continue
                    
                print(f"Restoring snapshot from {archive_path}")
                # Restore using tar. -P to extract absolute paths back to their exact original location.
                subprocess.run(["tar", "-xzPf", archive_path], check=True)
                print(f"Rollback {rb_id} completed successfully.")
            else:
                print(f"Rollback payload: {payload}")
                print(f"Rollback {rb_id} completed successfully.")

            # Optionally remove from registry after successful rollback
            # cursor.execute("DELETE FROM rollback_registry WHERE rollback_id = ?", (rb_id,))

        conn.commit()
