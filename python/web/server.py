"""FastAPI Web Server for SysClean Web UI."""
import os
import sqlite3
import json
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Use standard project DB path
DB_PATH = pathlib.Path.home() / ".local/share/sysclean/sysclean.db"

app = FastAPI(title="SysClean UI API")

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
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT operation_id, module, status, risk_level FROM queue ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        return [{"id": row["operation_id"], "module": row["module"], "status": row["status"], "risk": row["risk_level"]} for row in rows]
    finally:
        conn.close()

@app.get("/api/active")
def get_active():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT operation_id, module, status FROM queue WHERE status IN ('EXECUTING', 'VERIFYING') ORDER BY id DESC")
        rows = cursor.fetchall()
        return [{"id": row["operation_id"], "module": row["module"], "status": row["status"]} for row in rows]
    finally:
        conn.close()

@app.get("/api/rollbacks")
def get_rollbacks():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT rollback_id, module, rollback_type, created_at FROM rollback_registry ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        return [{"id": row["rollback_id"], "module": row["module"], "type": row["rollback_type"], "date": row["created_at"]} for row in rows]
    finally:
        conn.close()

@app.get("/api/storage")
def get_storage():
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
    finally:
        conn.close()

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
