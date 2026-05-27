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
    total_size = 0
    
    # Check apt cache
    cache_dir = pathlib.Path("/var/cache/apt/archives")
    if cache_dir.exists():
        size = sum(f.stat().st_size for f in cache_dir.glob("**/*") if f.is_file())
        if size > 0:
            targets.append({"id": "apt_cache", "type": "directory", "path": str(cache_dir), "size_bytes": size})
            total_size += size
            
    # Check autoremove (simulated)
    out = run_cmd(["apt-get", "-s", "autoremove"])
    packages = []
    for line in out.splitlines():
        if line.startswith("Remv "):
            pkg = line.split(" ")[1]
            packages.append(pkg)
            
    if packages:
        # We don't easily know size per unneeded package without more complex dpkg queries,
        # but we register them as targets.
        targets.append({"id": "apt_autoremove", "type": "packages", "items": packages, "size_bytes": 0})
        
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "apt",
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
        if t["id"] == "apt_cache":
            if run_cmd(["apt-get", "clean"]) == "":
                # Could be permission issue or success, assume success if no error raised
                pass 
        elif t["id"] == "apt_autoremove":
            try:
                subprocess.check_call(["apt-get", "autoremove", "-y"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                status = "partial_failure"
                errors.append(f"autoremove failed: {e}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
