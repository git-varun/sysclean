#!/usr/bin/env python3
import sys
import json
import subprocess
import pathlib
import os
import shutil
import time

TEMP_DIRS = [
    "/tmp",
    "/var/tmp"
]

AGE_THRESHOLD_DAYS = 3
AGE_THRESHOLD_SECONDS = AGE_THRESHOLD_DAYS * 24 * 60 * 60

def plan():
    targets = []
    total_size = 0
    now = time.time()
    
    for d in TEMP_DIRS:
        base_dir = pathlib.Path(d)
        if not base_dir.exists():
            continue
            
        try:
            for p in base_dir.iterdir():
                # Skip some system critical temp files/directories if any exist right at root
                if p.name.startswith("systemd-private-"):
                    continue
                    
                try:
                    stat = p.stat()
                    # Check age
                    if (now - stat.st_mtime) > AGE_THRESHOLD_SECONDS:
                        if p.is_file() or p.is_symlink():
                            size = stat.st_size
                            targets.append({
                                "id": f"temp_{p.name}",
                                "type": "file",
                                "path": str(p),
                                "size_bytes": size
                            })
                            total_size += size
                        elif p.is_dir():
                            # Very rough size estimation for directories
                            size = sum(f.stat().st_size for f in p.rglob('*') if f.is_file() and not f.is_symlink())
                            targets.append({
                                "id": f"temp_{p.name}",
                                "type": "directory",
                                "path": str(p),
                                "size_bytes": size
                            })
                            total_size += size
                except (PermissionError, FileNotFoundError):
                    pass
        except PermissionError:
            pass
            
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "tempfiles",
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
        p = pathlib.Path(t["path"])
        
        # Safety check: ensure it's actually within a temp dir
        is_safe = any(str(p).startswith(d + "/") for d in TEMP_DIRS)
        if not is_safe:
            status = "partial_failure"
            errors.append(f"Safety check failed for path: {p}")
            continue
            
        try:
            if t["type"] == "directory":
                subprocess.check_call(["sudo", "rm", "-rf", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.check_call(["sudo", "rm", "-f", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            status = "partial_failure"
            errors.append(f"failed to remove {p}: {e}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
