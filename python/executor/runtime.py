"""Module docstring."""
import subprocess
import time

from telemetry.events import emit_event
from rollback.engine import register_rollback


def execute_operation(operation):
    """Function docstring."""

    started = time.time()

    emit_event(
        "operation_started",
        operation
    )

    command = operation["command"]

    process = subprocess.run(
        command,
        capture_output=True,
        text=True
    )

    duration_ms = int(
        (time.time() - started) * 1000
    )

    emit_event(
        "operation_finished",
        {
            "operation": operation,
            "status": process.returncode,
            "duration_ms": duration_ms
        }
    )

    if process.returncode != 0:
        raise RuntimeError(process.stderr)

    register_rollback(operation)
