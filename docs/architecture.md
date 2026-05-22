# SysClean Architecture

SysClean operates on a robust, strict queue-based state machine and ensures absolute safety with deterministic rollback.

## Components
- **CLI (`sysclean-cli`)**: Enqueues tasks, monitors progress via read-only views.
- **Daemon (`syscleand`)**: Privileged runner executing approved tasks.
- **SQLite WAL**: transactional queue (`queue`), rollback history (`rollback_registry`), and telemetry (`telemetry_events`).

## Security
- UNIX Sockets for IPC.
- Immutable risk layers.
- Strict path canonicalization preventing directory traversal.
