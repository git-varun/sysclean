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
