import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from .models import QueueTask
from .db import SessionLocal

VALID_TRANSITIONS = {
    "PROPOSED": ["APPROVED", "FAILED"],
    "APPROVED": ["EXECUTING", "FAILED"],
    "EXECUTING": ["VERIFYING", "FAILED"],
    "VERIFYING": ["COMPLETED", "FAILED"],
    "COMPLETED": [],
    "FAILED": []
}

def enqueue(module: str, payload: dict, risk_level: str = "safe") -> str:
    operation_id = str(uuid.uuid4())
    db: Session = SessionLocal()
    try:
        task = QueueTask(
            operation_id=operation_id,
            module=module,
            phase="queued",
            status="PROPOSED",
            risk_level=risk_level,
            payload_json=payload
        )
        db.add(task)
        db.commit()
        return operation_id
    finally:
        db.close()

def transition_state(operation_id: str, new_status: str, expected_current_status: str = None) -> bool:
    """
    Atomic queue state transition using explicit transactions.
    """
    db: Session = SessionLocal()
    try:
        query = db.query(QueueTask).filter(QueueTask.operation_id == operation_id)
        if expected_current_status:
            if new_status not in VALID_TRANSITIONS.get(expected_current_status, []):
                return False
            query = query.filter(QueueTask.status == expected_current_status)
        else:
            # Need to verify transition is valid based on DB state if not provided
            task = query.first()
            if not task or new_status not in VALID_TRANSITIONS.get(task.status, []):
                return False
        
        updated_count = query.update({"status": new_status, "updated_at": datetime.now(timezone.utc)})
        db.commit()
        return updated_count > 0
    except OperationalError:
        db.rollback()
        return False
    finally:
        db.close()

def recover_crashed_tasks():
    """
    Crash recovery: Reset any EXECUTING or VERIFYING tasks to FAILED.
    This runs on daemon startup.
    """
    db: Session = SessionLocal()
    try:
        db.query(QueueTask).filter(QueueTask.status.in_(["EXECUTING", "VERIFYING"])).update(
            {"status": "FAILED", "updated_at": datetime.now(timezone.utc)}
        )
        db.commit()
    except OperationalError:
        db.rollback()
    finally:
        db.close()

def recover_stale_tasks(stale_minutes=30):
    """
    Stale execution recovery: Mark older EXECUTING/VERIFYING tasks as FAILED.
    """
    db: Session = SessionLocal()
    try:
        threshold = datetime.now(timezone.utc) - timedelta(minutes=stale_minutes)
        db.query(QueueTask).filter(
            QueueTask.status.in_(["EXECUTING", "VERIFYING"]),
            QueueTask.updated_at < threshold
        ).update({"status": "FAILED", "updated_at": datetime.now(timezone.utc)})
        db.commit()
    except OperationalError:
        db.rollback()
    finally:
        db.close()

