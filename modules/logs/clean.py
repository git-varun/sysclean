#!/usr/bin/env python3
import sys
import json
import subprocess
import pathlib

LOG_DIR = "/var/log"

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return ""

def plan():
    targets = []
    total_size = 0
    
    # 1. Rotated logs in /var/log
    base_dir = pathlib.Path(LOG_DIR)
    if base_dir.exists():
        try:
            for p in base_dir.rglob('*'):
                if p.is_file():
                    # Look for old rotated logs ending in .gz, .1, .2 etc
                    name = p.name
                    if name.endswith('.gz') or name.endswith('.old') or (len(name) > 2 and name[-2] == '.' and name[-1].isdigit()):
                        size = p.stat().st_size
                        targets.append({
                            "id": f"log_{p.name}",
                            "type": "file",
                            "path": str(p),
                            "size_bytes": size
                        })
                        total_size += size
        except PermissionError:
            pass
            
    # 2. Journalctl logs
    # We can check current journal usage
    out = run_cmd(["journalctl", "--disk-usage"])
    # Example output: Archived and active journals take up 2.0G in the file system.
    # We won't parse exact size easily without complex regex, we'll just add a generic target
    targets.append({
        "id": "journalctl_vacuum",
        "type": "journal",
        "action": "vacuum-time=7d",
        "size_bytes": 0 # Difficult to know exactly how much will be freed
    })
            
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "logs",
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
        if t["type"] == "file":
            p = pathlib.Path(t["path"])
            
            # Safety check: ensure it's actually within /var/log
            if not str(p).startswith(LOG_DIR + "/"):
                status = "partial_failure"
                errors.append(f"Safety check failed for path: {p}")
                continue
                
            try:
                subprocess.check_call(["sudo", "rm", "-f", str(p)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                status = "partial_failure"
                errors.append(f"failed to remove {p}: {e}")
                
        elif t["type"] == "journal":
            try:
                subprocess.check_call(["sudo", "journalctl", f"--{t['action']}"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception as e:
                status = "partial_failure"
                errors.append(f"failed to vacuum journal: {e}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
