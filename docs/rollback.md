# SysClean Rollback Mechanics

SysClean guarantees reversibility of destructive operations where possible. This is managed by the `rollback_registry` system.

## Supported Methods
1. **Snapshot-based (`rollback_type="snapshot"`)**: Archives specific directories (e.g., caches, tempfiles) to a `.tar.gz` before deletion. During rollback, the archive is simply extracted to the original absolute path.
2. **Command-based (`rollback_type="command"`)**: For targets like APT and Docker, a script or inverse command sequence is retained (e.g., `apt-get install <deleted_packages>`). 

## Execution
To perform a rollback, the user must specify the operation ID from the queue.
```bash
sysclean-cli rollback <operation_id>
```

When triggered, the daemon locates the `rollback_registry` entry, determines the rollback method, and executes the inverse operations or unzips the snapshots.
