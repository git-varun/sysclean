"""Module docstring."""
import subprocess
import time

from queue_engine.events import emit_event
from core.engine import register_rollback, create_snapshot
from security.validation import validate_operation


class CommandExecutionError(RuntimeError):
    """Structured error for command execution failures."""
    pass


class CommandTimeoutError(RuntimeError):
    """Structured error for command execution timeouts."""
    pass


def execute_operation(operation):
    """Function docstring."""

    # Security validation
    try:
        validate_operation(operation)
    except Exception as exc:
        raise CommandExecutionError(f"Security validation failed: {exc}") from exc

    started = time.time()

    emit_event(
        "operation_started",
        operation
    )

    command = operation["command"]
    
    if not isinstance(command, list):
        raise ValueError("Command must be a list, not a string.")

    # Snapshot Phase
    snapshot_metadata = None
    targets = operation.get("targets", [])
    if targets:
        operation_id = operation.get("id", "unknown")
        snapshot_metadata = create_snapshot(operation_id, targets)

    timeout_seconds = operation.get("timeout", 300)

    try:
        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,  # configurable subprocess timeout
            check=False
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.time() - started) * 1000)
        emit_event(
            "operation_finished",
            {
                "operation": operation,
                "status": -1,
                "duration_ms": duration_ms,
                "error": "TimeoutExpired"
            }
        )
        raise CommandTimeoutError(f"Command timed out after {timeout_seconds} seconds: {command}") from exc
    except Exception as exc:
        duration_ms = int((time.time() - started) * 1000)
        emit_event(
            "operation_finished",
            {
                "operation": operation,
                "status": -1,
                "duration_ms": duration_ms,
                "error": str(exc)
            }
        )
        raise CommandExecutionError(f"Command execution failed: {exc}") from exc

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
        raise CommandExecutionError(process.stderr)

    register_rollback(operation, snapshot_metadata)
