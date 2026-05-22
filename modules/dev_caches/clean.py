#!/usr/bin/env python3
import sys
import json
import subprocess
import pathlib
import os
import shutil

CACHE_DIRS = [
    ".npm/_cacache",
    ".cache/pip",
    ".cache/yarn",
    ".cache/go-build"
]

def get_dir_size(path):
    total = 0
    try:
        for p in path.rglob('*'):
            if p.is_file():
                total += p.stat().st_size
    except PermissionError:
        pass
    return total

def plan():
    targets = []
    total_size = 0
    
    home = pathlib.Path.home()
    
    for c in CACHE_DIRS:
        d = home / c
        if d.exists() and d.is_dir():
            size = get_dir_size(d)
            if size > 0:
                targets.append({
                    "id": f"dev_cache_{c.replace('/', '_')}",
                    "type": "directory",
                    "path": str(d),
                    "size_bytes": size
                })
                total_size += size
                
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "dev_caches",
        "targets": targets,
        "command": [sys.executable, script_path, "--execute"],
        "estimated_bytes": total_size
    }

def execute():
    try:
        input_data = json.load(sys.stdin)
        targets = input_data.get("targets", [])
    except json.JSONDecodeError:
        targets = []
        
    status = "success"
    errors = []
    
    for t in targets:
        if t["type"] == "directory":
            p = pathlib.Path(t["path"])
            # Safety check: only delete if it's within the home directory and has 'cache' or 'npm' in path
            # to prevent catastrophic accidental deletion if JSON is malformed
            if str(pathlib.Path.home()) in str(p) and ('cache' in str(p).lower() or 'npm' in str(p).lower()):
                try:
                    shutil.rmtree(p)
                except Exception as e:
                    status = "partial_failure"
                    errors.append(f"failed to remove {p}: {e}")
            else:
                status = "partial_failure"
                errors.append(f"Safety check failed for path: {p}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
