import os
import sqlite3
import pytest
import time
import signal
import threading
import multiprocessing
from pathlib import Path
from datetime import datetime, timedelta

from queue_engine.db import DB_PATH, get_db, SessionLocal
from queue_engine.queue import enqueue, transition_state, recover_crashed_tasks, VALID_TRANSITIONS, recover_stale_tasks
from queue_engine.models import QueueTask, Base
from core.runtime import execute_operation, CommandExecutionError
from core.engine import register_rollback, create_snapshot

# Setup test DB safely for concurrent tests
@pytest.fixture(autouse=True)
def setup_db():
    from queue_engine.db import engine
    from queue_engine.models import Base
    
    Base.metadata.create_all(bind=engine)
    
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
            
    yield

def _concurrent_worker(worker_id):
    """Worker function for concurrent queue access test."""
    try:
        # Enqueue 5 items per worker
        op_ids = []
        for i in range(5):
            op_id = enqueue(f"module_{worker_id}_{i}", {"data": "test"})
            op_ids.append(op_id)
            
        # Try to transition them simultaneously
        for op_id in op_ids:
            transition_state(op_id, "APPROVED", "PROPOSED")
            transition_state(op_id, "EXECUTING", "APPROVED")
            transition_state(op_id, "VERIFYING", "EXECUTING")
            transition_state(op_id, "COMPLETED", "VERIFYING")
    except Exception as e:
        print(f"Worker {worker_id} failed: {e}")

def test_concurrent_queue_access():
    """Test SQLite WAL concurrency handling."""
    threads = []
    # Start 10 concurrent threads
    for i in range(10):
        t = threading.Thread(target=_concurrent_worker, args=(i,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    db = SessionLocal()
    completed_tasks = db.query(QueueTask).filter(QueueTask.status == "COMPLETED").count()
    db.close()
    
    # 10 workers * 5 tasks = 50 completed tasks
    assert completed_tasks == 50

def _crash_worker(op_id):
    """Worker that simulates daemon work but hangs, waiting to be killed."""
    from queue_engine.db import engine
    engine.dispose()
    transition_state(op_id, "APPROVED", "PROPOSED")
    transition_state(op_id, "EXECUTING", "APPROVED")
    # Simulate a hanging operation (e.g. docker pull hanging indefinitely)
    time.sleep(10)

def test_daemon_crash_recovery():
    """Simulate a SIGKILL (kill -9) daemon crash while executing."""
    op_id = enqueue("crash_module", {})
    
    # Spawn process to do the work
    p = multiprocessing.Process(target=_crash_worker, args=(op_id,))
    p.start()
    
    # Give it time to transition to EXECUTING
    time.sleep(2.0)
    
    # Verify it is executing
    db = SessionLocal()
    task = db.query(QueueTask).filter(QueueTask.operation_id == op_id).first()
    assert task.status == "EXECUTING"
    db.close()
    
    # Hard kill the process (kill -9)
    os.kill(p.pid, signal.SIGKILL)
    p.join()
    
    # Run recovery (this is called when daemon restarts)
    recover_crashed_tasks()
    
    # Verify the task was cleanly aborted to FAILED
    db = SessionLocal()
    task = db.query(QueueTask).filter(QueueTask.operation_id == op_id).first()
    assert task.status == "FAILED"
    db.close()

def test_stale_task_recovery():
    """Test recovery of tasks that stalled due to power interruption / time drift."""
    op_id = enqueue("stale_module", {})
    
    # Force state to EXECUTING and manually modify the timestamp to 45 minutes ago
    transition_state(op_id, "APPROVED", "PROPOSED")
    transition_state(op_id, "EXECUTING", "APPROVED")
    
    db = SessionLocal()
    task = db.query(QueueTask).filter(QueueTask.operation_id == op_id).first()
    # Mock timestamp to 45 minutes ago
    from datetime import timezone
    task.updated_at = datetime.now(timezone.utc) - timedelta(minutes=45)
    db.commit()
    db.close()
    
    # Stale threshold is 30 minutes by default
    recover_stale_tasks(stale_minutes=30)
    
    db = SessionLocal()
    task = db.query(QueueTask).filter(QueueTask.operation_id == op_id).first()
    assert task.status == "FAILED"
    db.close()

def test_rollback_partial_failure(tmp_path):
    """Test rollback integrity if an execution fails halfway."""
    # Create two test files
    file1 = tmp_path / "target1.txt"
    file2 = tmp_path / "target2.txt"
    file1.write_text("data1")
    file2.write_text("data2")
    
    op_id = enqueue("test_module", {"targets": [str(file1), str(file2)]})
    
    # Create snapshot of both files
    metadata = create_snapshot(op_id, [str(file1), str(file2)])
    register_rollback({"id": op_id, "module": "test"}, metadata)
    
    # Delete the first file (simulating partial execution)
    os.remove(file1)
    
    # Simulate a crash before deleting file2
    # State goes FAILED
    transition_state(op_id, "FAILED", "PROPOSED") # Simplified path for test
    
    # Run rollback
    from core.engine import execute_rollback
    execute_rollback()
    
    # file1 should be restored perfectly
    assert file1.exists()
    assert file1.read_text() == "data1"
    # file2 should still exist
    assert file2.exists()
    assert file2.read_text() == "data2"
