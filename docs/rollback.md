# SysClean Rollback Mechanics

SysClean guarantees reversibility of destructive operations where possible. This is managed by the `rollback_registry` database table.

## Supported Methods
1. **Snapshot-based (`rollback_type="snapshot"`)**: Archives specific directories (e.g., caches, tempfiles) to a `.tar.gz` archive before deletion. During rollback, the archive is simply extracted to the original absolute path.
2. **Command-based (`rollback_type="command"`)**: For targets like APT and Docker, a script or inverse command sequence is retained (e.g., `apt-get install <deleted_packages>`). 

## Execution & Registry Tracking
To perform a rollback, the user can review recorded metadata archives on the SysClean Web UI:
- **Registry Logs:** The Web dashboard lists all successful cleanups registered in the database, showing the module name, type of rollback, and creation date.
- **Rollback Operation:** When triggered via the backend runner, the engine locates the corresponding `rollback_registry` entry, determines the rollback method, and executes the inverse operations or extracts the snapshots.

