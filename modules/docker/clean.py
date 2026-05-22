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
    
    # Check dangling images
    out = run_cmd(["sudo", "docker", "images", "-f", "dangling=true", "-q"])
    dangling_images = [img for img in out.splitlines() if img.strip()]
    if dangling_images:
        targets.append({"id": "docker_dangling_images", "type": "images", "items": dangling_images, "size_bytes": 0})
        
    # Check exited containers
    out = run_cmd(["sudo", "docker", "ps", "-a", "-f", "status=exited", "-q"])
    exited_containers = [c for c in out.splitlines() if c.strip()]
    if exited_containers:
        targets.append({"id": "docker_exited_containers", "type": "containers", "items": exited_containers, "size_bytes": 0})
        
    script_path = str(pathlib.Path(__file__).resolve())
    return {
        "module": "docker",
        "targets": targets,
        "command": [sys.executable, script_path, "--execute"],
        "estimated_bytes": total_size # We could parse docker system df for exact sizes, but omitting for brevity
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
        if t["id"] == "docker_dangling_images" and t["items"]:
            try:
                subprocess.check_call(["sudo", "docker", "rmi"] + t["items"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                status = "partial_failure"
                errors.append(f"failed to remove some images: {e}")
                
        elif t["id"] == "docker_exited_containers" and t["items"]:
            try:
                subprocess.check_call(["sudo", "docker", "rm"] + t["items"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except subprocess.CalledProcessError as e:
                status = "partial_failure"
                errors.append(f"failed to remove some containers: {e}")
                
    return {"status": status, "errors": errors}

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--plan":
        print(json.dumps(plan(), indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "--execute":
        print(json.dumps(execute(), indent=2))
    else:
        print(json.dumps({"error": "Invalid arguments. Use --plan or --execute"}))
        sys.exit(1)
