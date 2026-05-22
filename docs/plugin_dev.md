# SysClean Plugin Developer Guide

SysClean follows a strict `--plan` and `--execute` contract for all cleanup plugins. 

## The Plugin Contract

### 1. Planning Phase (`--plan`)
When a plugin is invoked with `--plan`, it must output a JSON object containing the expected cleanup targets, but **it must not modify the system**.
```json
{
    "module": "tempfiles",
    "targets": [
        {
            "id": "tmp_dir_1",
            "type": "directory",
            "path": "/tmp/stale_cache",
            "size_bytes": 1048576
        }
    ],
    "command": ["python3", "/path/to/plugin.py", "--execute"],
    "estimated_bytes": 1048576
}
```

### 2. Execution Phase (`--execute`)
When a plugin is invoked with `--execute`, it receives the JSON plan via `stdin`. It is only permitted to operate on the targets provided in the `stdin` payload.
**Rule:** No broad or generalized discovery during execution. Execute exactly what was planned.

## Security Constraints
Any targets defined in the plan are sent to `syscleand` and subjected to the Validation Engine (`python/security/validation.py`). If your plugin targets `~/.ssh` or other protected assets, the daemon will permanently fail the task.
