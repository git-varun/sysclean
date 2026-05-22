import os
import sys
import uuid
import json
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "python")))

from queue_engine.db import engine, SessionLocal
from queue_engine.models import QueueTask, RollbackRegistry, Base
from queue_engine.events import emit_event

def populate():
    Base.metadata.create_all(engine)
    db = SessionLocal()
    
    # Create some proposed tasks
    t1 = QueueTask(
        module="apt",
        phase="queued",
        status="PROPOSED",
        risk_level="safe",
        payload_json={"estimated_bytes": 1024 * 1024 * 500} # 500MB
    )
    t2 = QueueTask(
        module="docker",
        phase="queued",
        status="APPROVED",
        risk_level="balanced",
        payload_json={"estimated_bytes": 1024 * 1024 * 1024 * 2} # 2GB
    )
    t3 = QueueTask(
        module="snap",
        phase="queued",
        status="EXECUTING",
        risk_level="aggressive",
        payload_json={"estimated_bytes": 1024 * 1024 * 300} # 300MB
    )
    t4 = QueueTask(
        module="logs",
        phase="queued",
        status="COMPLETED",
        risk_level="safe",
        payload_json={"estimated_bytes": 1024 * 1024 * 10} # 10MB
    )
    
    db.add_all([t1, t2, t3, t4])
    
    # Create some mock rollbacks
    rb1 = RollbackRegistry(
        operation_id=str(uuid.uuid4()),
        module="apt",
        rollback_type="snapshot",
        rollback_payload="{}"
    )
    rb2 = RollbackRegistry(
        operation_id=str(uuid.uuid4()),
        module="docker",
        rollback_type="command",
        rollback_payload='{"cmd": "docker start x"}'
    )
    db.add_all([rb1, rb2])
    
    db.commit()
    db.close()
    
    # Emit some telemetry events
    emit_event("sysclean_startup", {"version": "1.0"})
    emit_event("operation_started", {"module": "snap"})
    time.sleep(1) # give the background thread a moment to flush the event log

if __name__ == "__main__":
    populate()
    print("Mock data populated.")
