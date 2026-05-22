#!/usr/bin/env python3
import sys
import json
import subprocess
import pathlib

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, text=True, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        return ""

def plan():
    targets = []
    
    # Snap list --all shows disabled snaps which are old revisions
    out = run_cmd(["snap", "list", "--all"])
    for line in out.splitlines()[1:]: # Skip header
        parts = line.split()
        if len(parts) >= 6 and parts[-1] == "disabled":
            name = parts[0]
            revision = parts[2]
            targets.append({
                "id": f"snap_{name}_{revision}",
                "type": "snap_revision",
                "name": name,
                "revision": revision,
                "size_bytes": 0
            })
            
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "snap",
        "targets": targets,
        "command": [sys.executable, script_path, "--execute"],
        "estimated_bytes": 0 # Difficult to parse size precisely from snap list
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
        if t["type"] == "snap_revision":
            name = t["name"]
            revision = t["revision"]
            try:
                subprocess.check_call(["sudo", "snap", "remove", name, "--revision", revision], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                status = "partial_failure"
                errors.append(f"failed to remove snap {name} revision {revision}: {e}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
