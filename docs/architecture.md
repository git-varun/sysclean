# SysClean Architecture

SysClean implements a strictly isolated, state-machine-driven architecture designed to manage automated and user-directed system cleanups with safety guarantees.

## Client-Daemon Separation
SysClean is composed of two primary components:
1. **`syscleand` (Daemon):** Runs as a privileged background process. It hosts an execution engine and state machine built on a high-concurrency SQLite WAL database.
2. **`sysclean-cli` (Client):** A user-facing command line and textual interface (TUI) running as an unprivileged user. It issues requests (via Unix Domain Socket IPC or direct DB enqueuing if privileged) to the daemon.

## Queue Engine (State Machine)
All operations pass through a strict state machine:
`PROPOSED` → `APPROVED` → `EXECUTING` → `VERIFYING` → `COMPLETED` | `FAILED`

The queue engine automatically handles crash recovery by identifying `EXECUTING` tasks on startup and failing them. Stale tasks are routinely cleared.

## Security & Isolation
- **Validation**: Strict validation prevents deletion of `.ssh`, `.gnupg`, and other protected files/directories.
- **Rollback**: Snapshot-based rollback capabilities compress target metadata/files before destructive operations proceed.
- **AI Bound**: The AI Advisory Engine (`python/ai/advisory.py`) is granted explicit boundaries: it can synthesize and recommend, but cannot execute or bypass the queue validation layer.
