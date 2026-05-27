"""Module docstring."""
import subprocess
import time

from queue_engine.events import emit_event
from core.engine import register_rollback, create_snapshot
from security.validation import validate_operation
from core.logger import get_logger

logger = get_logger("sysclean.runtime")

class CommandExecutionError(RuntimeError):
    """Structured error for command execution failures."""
    pass


class CommandTimeoutError(RuntimeError):
    """Structured error for command execution timeouts."""
    pass


def execute_operation(operation):
    """Function docstring."""
    operation_id = operation.get("id", "unknown")
    module_name = operation.get("module", "unknown")
    
    logger.info(f"Starting execution for operation {operation_id} (Module: {module_name})")

    # Security validation
    try:
        logger.debug(f"Validating operation {operation_id}")
        validate_operation(operation)
        logger.debug(f"Validation passed for {operation_id}")
    except Exception as exc:
        logger.error(f"Security validation failed for {operation_id}: {exc}")
        raise CommandExecutionError(f"Security validation failed: {exc}") from exc

    started = time.time()

    emit_event(
        "operation_started",
        operation
    )
    logger.debug(f"Emitted 'operation_started' event for {operation_id}")

    command = operation["command"]
    
    if not isinstance(command, list):
        logger.error(f"Invalid command format for {operation_id}: expected list, got {type(command)}")
        raise ValueError("Command must be a list, not a string.")

    import os
    if os.geteuid() != 0 and command[0] != "pkexec":
        logger.info(f"Non-root environment detected. Prepending pkexec to {operation_id} command")
        command = ["pkexec"] + command

    # Snapshot Phase
    snapshot_metadata = None
    targets = operation.get("targets", [])
    if targets:
        logger.info(f"Creating snapshot for targets: {targets}")
        snapshot_metadata = create_snapshot(operation_id, targets)
        logger.debug(f"Snapshot created successfully for {operation_id}")
    else:
        logger.debug(f"No snapshot targets specified for {operation_id}")

    timeout_seconds = operation.get("timeout", 300)

    import json
    logger.info(f"Executing command for {operation_id}: {' '.join(command)}")
    try:
        process = subprocess.run(
            command,
            input=json.dumps(operation),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,  # configurable subprocess timeout
            check=False
        )
    except subprocess.TimeoutExpired as exc:
        duration_ms = int((time.time() - started) * 1000)
        logger.error(f"Command execution timed out after {timeout_seconds}s for {operation_id}")
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
        logger.error(f"Command execution failed abruptly for {operation_id}: {exc}")
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

    logger.debug(f"Command for {operation_id} returned code {process.returncode} in {duration_ms}ms")
    if process.stdout:
        logger.debug(f"STDOUT for {operation_id}: {process.stdout.strip()}")
    if process.stderr:
        logger.warning(f"STDERR for {operation_id}: {process.stderr.strip()}")

    emit_event(
        "operation_finished",
        {
            "operation": operation,
            "status": process.returncode,
            "duration_ms": duration_ms
        }
    )

    if process.returncode != 0:
        logger.error(f"Operation {operation_id} failed with exit code {process.returncode}")
        raise CommandExecutionError(process.stderr)

    logger.info(f"Operation {operation_id} completed successfully. Registering rollback metadata.")
    register_rollback(operation, snapshot_metadata)
