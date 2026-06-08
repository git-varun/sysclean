"""FastAPI Web Server for SysClean Web UI."""
import os
import sqlite3
import json
import pathlib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import subprocess
import sys
import asyncio
from core.client import send_operation
from core.logger import get_logger
from ai.advisory import AdvisoryEngine

logger = get_logger("sysclean.web")

# Use standard project DB path
DB_PATH = pathlib.Path.home() / ".local/share/sysclean/sysclean.db"

app = FastAPI(title="SysClean UI API")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting SysClean Web UI server")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down SysClean Web UI server")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    # Use read-only URI if possible, fallback to standard
    if not DB_PATH.exists():
        return None
    try:
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception:
        # Fallback if URI not supported or file issues
        try:
            conn = sqlite3.connect(str(DB_PATH))
            conn.row_factory = sqlite3.Row
            return conn
        except:
            return None

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/queue")
def get_queue():
    logger.debug("Fetching operation queue")
    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed while fetching queue")
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT operation_id, module, status, risk_level FROM queue ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        return [{"id": row["operation_id"], "module": row["module"], "status": row["status"], "risk": row["risk_level"]} for row in rows]
    except Exception as e:
        logger.error(f"Error fetching queue: {e}")
        return []
    finally:
        conn.close()

@app.get("/api/active")
def get_active():
    logger.debug("Fetching active executions")
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT operation_id, module, status FROM queue WHERE status IN ('EXECUTING', 'VERIFYING') ORDER BY id DESC")
        rows = cursor.fetchall()
        return [{"id": row["operation_id"], "module": row["module"], "status": row["status"]} for row in rows]
    except Exception as e:
        logger.error(f"Error fetching active executions: {e}")
        return []
    finally:
        conn.close()

@app.get("/api/rollbacks")
def get_rollbacks():
    logger.debug("Fetching rollback registry")
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT rollback_id, module, rollback_type, created_at FROM rollback_registry ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        return [{"id": row["rollback_id"], "module": row["module"], "type": row["rollback_type"], "date": row["created_at"]} for row in rows]
    except Exception as e:
        logger.error(f"Error fetching rollbacks: {e}")
        return []
    finally:
        conn.close()

@app.get("/api/storage")
def get_storage():
    logger.debug("Fetching storage savings")
    conn = get_db_connection()
    if not conn:
        return {"reclaimable_bytes": 0}
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT payload_json FROM queue WHERE status IN ('PROPOSED', 'APPROVED', 'EXECUTING')")
        payloads = cursor.fetchall()
        total_reclaimable = 0
        for row in payloads:
            payload_str = row["payload_json"]
            if payload_str:
                try:
                    data = json.loads(payload_str)
                    total_reclaimable += data.get("estimated_bytes", 0)
                except json.JSONDecodeError:
                    pass
        return {"reclaimable_bytes": total_reclaimable}
    except Exception as e:
        logger.error(f"Error fetching storage: {e}")
        return {"reclaimable_bytes": 0}
    finally:
        conn.close()

@app.get("/api/advise/{target}")
def advise_target(target: str):
    logger.info(f"Received AI Advisory request for target: {target}")
    try:
        engine = AdvisoryEngine()
        if target == "docker":
            res = engine.analyze_docker_resources()
        elif target == "apt":
            res = engine.analyze_apt_packages()
        elif target == "storage":
            res = engine.estimate_reclaimable_storage()
        else:
            raise HTTPException(status_code=400, detail=f"Unknown target: {target}")
            
        if isinstance(res, dict) and "error" in res:
            logger.error(f"AI Provider error: {res['error']}")
            raise HTTPException(status_code=503, detail=res["error"])
            
        return {"status": "success", "recommendation": res.get("response", res) if isinstance(res, dict) else res}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate AI advisory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class EnqueueRequest(BaseModel):
    plans: List[Dict[Any, Any]]

def enrich_target(module: str, target: dict) -> dict:
    name = target.get("id", "unknown")
    service = module
    
    if "path" in target:
        path_str = target["path"]
        name = os.path.basename(path_str)
        
        if "/.npm" in path_str:
            service = "npm"
        elif "/.cache/pip" in path_str:
            service = "pip"
        elif "/.cache/" in path_str:
            parts = path_str.split("/.cache/")
            if len(parts) > 1:
                service = parts[1].split("/")[0]
        elif "/var/log" in path_str:
            parts = path_str.split("/var/log/")
            if len(parts) > 1:
                subparts = parts[1].split("/")
                if len(subparts) > 1:
                    service = subparts[0]
                else:
                    log_name = subparts[0]
                    if log_name.startswith("syslog"):
                        service = "syslog"
                    elif log_name.startswith("dpkg"):
                        service = "dpkg"
                    elif log_name.startswith("kern"):
                        service = "kernel"
                    elif log_name.startswith("auth"):
                        service = "auth"
                    elif log_name.startswith("udev"):
                        service = "udev"
                        
    elif module == "apt" and target.get("id") == "apt_autoremove":
        service = "apt"
        name = "Autoremove packages"
    elif module == "snap":
        service = "snap"
        name = f"{target.get('name', '')} (rev {target.get('revision', '')})"
        
    target["service"] = service
    target["display_name"] = name
    return target

@app.post("/api/scan/plan")
async def scan_plan():
    """Run all module planners and return the generated plans."""
    logger.info("Initiating system scan planning phase")
    modules = ["apt", "docker", "snap", "dev_caches", "logs", "tempfiles"]
    root_dir = pathlib.Path(__file__).parent.parent.parent.resolve()
    
    plans = []
    for module in modules:
        script_path = root_dir / "modules" / module / "clean.py"
        if not script_path.exists():
            logger.warning(f"Planner script for {module} not found at {script_path}")
            continue
            
        logger.debug(f"Executing planner for {module}")
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, str(script_path), "--plan",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0 and stdout:
                plan_json = stdout.decode().strip()
                logger.debug(f"Planner {module} succeeded. Output size: {len(plan_json)} bytes")
                if plan_json:
                    try:
                        plan_data = json.loads(plan_json)
                        if "command" in plan_data:
                            plan_data["targets"] = [enrich_target(module, t) for t in plan_data.get("targets", [])]
                            plans.append(plan_data)
                            logger.info(f"Successfully generated plan for {module}")
                        else:
                            logger.error(f"Plan for {module} missing 'command' field")
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to decode JSON plan for {module}: {e}")
            else:
                logger.error(f"Planner {module} failed with code {proc.returncode}. Stderr: {stderr.decode().strip()}")
        except Exception as e:
            logger.error(f"Exception while planning {module}: {e}")
            
    logger.info(f"Scan planning completed. Generated {len(plans)} actionable plans.")
    return {"plans": plans}

@app.post("/api/scan/enqueue")
def scan_enqueue(request: EnqueueRequest):
    """Receive approved plans and send them to the daemon."""
    logger.info(f"Received request to enqueue {len(request.plans)} plans")
    for plan in request.plans:
        module_name = plan.get("module", "unknown")
        try:
            logger.debug(f"Enqueuing operation for module: {module_name}")
            send_operation(plan)
            logger.info(f"Successfully enqueued operation for {module_name}")
        except Exception as e:
            logger.error(f"Failed to enqueue operation for {module_name}: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to enqueue: {str(e)}")
    
    logger.info("Enqueue phase completed successfully")
    return {"status": "success", "enqueued": len(request.plans)}

@app.post("/api/rollback/{rollback_id}")
def trigger_rollback(rollback_id: str):
    """Trigger rollback for a specific rollback ID."""
    logger.info(f"Received request to execute rollback: {rollback_id}")
    try:
        from core.engine import execute_rollback
        execute_rollback(rollback_id)
        logger.info(f"Rollback {rollback_id} executed successfully")
        return {"status": "success", "message": f"Rollback {rollback_id} executed successfully"}
    except Exception as e:
        logger.error(f"Failed to execute rollback {rollback_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_docker_cmd(cmd: list) -> str:
    try:
        # Prepend pkexec if running as non-root
        full_cmd = ["pkexec"] + cmd if os.geteuid() != 0 else cmd
        return subprocess.check_output(full_cmd, text=True, stderr=subprocess.DEVNULL)
    except Exception as e:
        logger.error(f"Failed to run docker command {cmd}: {e}")
        return ""

@app.get("/api/docker/status")
def get_docker_status():
    logger.debug("Fetching Docker system status")
    
    # 1. Containers list
    out_ps = run_docker_cmd(["docker", "ps", "-a", "--format", '{"ID":"{{.ID}}","Names":"{{.Names}}","Image":"{{.Image}}","Status":"{{.Status}}","State":"{{.State}}","Ports":"{{.Ports}}"}'])
    containers = []
    for line in out_ps.splitlines():
        if line.strip():
            try:
                containers.append(json.loads(line))
            except Exception as e:
                logger.debug(f"Failed to parse container line: {line}. Error: {e}")
                
    # 2. Container stats (CPU & Memory)
    out_stats = run_docker_cmd(["docker", "stats", "--no-stream", "--format", '{"ID":"{{.ID}}","CPUPerc":"{{.CPUPerc}}","MemUsage":"{{.MemUsage}}"}'])
    stats_map = {}
    for line in out_stats.splitlines():
        if line.strip():
            try:
                stat = json.loads(line)
                stats_map[stat["ID"]] = stat
            except Exception as e:
                logger.debug(f"Failed to parse stats line: {line}. Error: {e}")
                
    # Merge Stats
    for c in containers:
        short_id = c["ID"][:12]
        stat = stats_map.get(short_id) or stats_map.get(c["ID"])
        if stat:
            c["cpu"] = stat.get("CPUPerc", "0.00%")
            c["memory"] = stat.get("MemUsage", "0B / 0B")
        else:
            c["cpu"] = "0.00%"
            c["memory"] = "0B / 0B"
            
    # 3. Images list
    out_imgs = run_docker_cmd(["docker", "images", "--format", '{"ID":"{{.ID}}","Repository":"{{.Repository}}","Tag":"{{.Tag}}","Size":"{{.Size}}","CreatedAt":"{{.CreatedAt}}"}'])
    images = []
    for line in out_imgs.splitlines():
        if line.strip():
            try:
                img = json.loads(line)
                img["dangling"] = (img["Repository"] == "<none>" or img["Tag"] == "<none>")
                images.append(img)
            except:
                pass
                
    # 4. Networks list
    out_nets = run_docker_cmd(["docker", "network", "ls", "--format", '{"ID":"{{.ID}}","Name":"{{.Name}}","Driver":"{{.Driver}}","Scope":"{{.Scope}}"}'])
    networks = []
    for line in out_nets.splitlines():
        if line.strip():
            try:
                networks.append(json.loads(line))
            except:
                pass
                
    # 5. Volumes list
    out_vols = run_docker_cmd(["docker", "volume", "ls", "--format", '{"Name":"{{.Name}}","Driver":"{{.Driver}}"}'])
    volumes = []
    for line in out_vols.splitlines():
        if line.strip():
            try:
                volumes.append(json.loads(line))
            except:
                pass
                
    # 6. Builder Cache footprint
    out_df = run_docker_cmd(["docker", "system", "df", "--format", "{{json .}}"])
    builder = {"size": "0B", "reclaimable": "0B (0%)", "count": 0}
    for line in out_df.splitlines():
        if line.strip():
            try:
                info = json.loads(line)
                if info.get("Type") == "Build Cache":
                    builder["size"] = info.get("Size", "0B")
                    builder["reclaimable"] = info.get("Reclaimable", "0B (0%)")
                    builder["count"] = int(info.get("TotalCount", 0))
            except:
                pass
                
    return {
        "status": "success",
        "containers": containers,
        "images": images,
        "networks": networks,
        "volumes": volumes,
        "builder": builder
    }

@app.get("/api/docker/container/logs/{id}")
def get_container_logs(id: str):
    logger.debug(f"Fetching logs for container {id}")
    logs = run_docker_cmd(["docker", "logs", "--tail", "100", id])
    return {"status": "success", "logs": logs}

@app.post("/api/docker/container/{action}/{id}")
def manage_container(action: str, id: str):
    logger.info(f"Container action {action} requested for {id}")
    if action not in ["start", "stop", "restart", "remove"]:
        raise HTTPException(status_code=400, detail="Invalid action")
        
    cmd = ["docker", action, id]
    if action == "remove":
        cmd = ["docker", "rm", "-f", id]
        
    res = run_docker_cmd(cmd)
    return {"status": "success", "output": res}

@app.post("/api/docker/image/remove/{id}")
def remove_image(id: str):
    logger.info(f"Image deletion requested for {id}")
    res = run_docker_cmd(["docker", "rmi", "-f", id])
    return {"status": "success", "output": res}

@app.post("/api/docker/clean/{category}")
def prune_docker(category: str):
    logger.info(f"Docker clean/prune requested for {category}")
    if category == "containers":
        res = run_docker_cmd(["docker", "container", "prune", "-f"])
    elif category == "images":
        res = run_docker_cmd(["docker", "image", "prune", "-f"])
    elif category == "networks":
        res = run_docker_cmd(["docker", "network", "prune", "-f"])
    elif category == "volumes":
        res = run_docker_cmd(["docker", "volume", "prune", "-f"])
    elif category == "builder":
        res = run_docker_cmd(["docker", "builder", "prune", "-f"])
    else:
        raise HTTPException(status_code=400, detail="Invalid category")
        
    return {"status": "success", "output": res}

# Mount Static Files (React Build)
# We calculate the path dynamically from this file's location to the project root/ui/dist
current_dir = pathlib.Path(__file__).parent.resolve()
ui_dist_path = current_dir.parent.parent / "ui" / "dist"

if ui_dist_path.exists():
    app.mount("/assets", StaticFiles(directory=str(ui_dist_path / "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Allow requests to API endpoints to fall through
        if full_path.startswith("api/"):
            return {"error": "Not found"}
        
        # Serve standard static files if requested (like vite.svg or favicon)
        static_file = ui_dist_path / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
            
        # Fallback to index.html for client-side routing
        return FileResponse(str(ui_dist_path / "index.html"))
