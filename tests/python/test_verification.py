import os
import sqlite3
import pytest
import time
from pathlib import Path
from datetime import datetime

from queue_engine.db import DB_PATH, get_db
from queue_engine.queue import enqueue, transition_state, recover_crashed_tasks, VALID_TRANSITIONS
from queue_engine.models import QueueTask, Base
from core.runtime import execute_operation, CommandExecutionError
from core.engine import register_rollback, create_snapshot

# Setup test DB
@pytest.fixture(autouse=True)
def setup_db():
    from queue_engine.db import engine
    from queue_engine.models import Base
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Clear all data from tables before each test
    with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
            
    yield

def test_queue_state_machine():
    op_id = enqueue("test_module", {"command": ["echo", "test"]})
    
    # Valid transition
    assert transition_state(op_id, "APPROVED", "PROPOSED") is True
    assert transition_state(op_id, "EXECUTING", "APPROVED") is True
    
    # Invalid transition (EXECUTING -> COMPLETED is not in VALID_TRANSITIONS directly)
    assert transition_state(op_id, "COMPLETED", "EXECUTING") is False
    
    # Strict path check: PROPOSED -> EXECUTING should fail
    assert transition_state(op_id, "EXECUTING", "PROPOSED") is False
    
    # Valid recovery transition
    assert transition_state(op_id, "FAILED", "EXECUTING") is True

def test_crash_recovery():
    op_id1 = enqueue("mod1", {})
    op_id2 = enqueue("mod2", {})
    
    transition_state(op_id1, "APPROVED", "PROPOSED")
    transition_state(op_id1, "EXECUTING", "APPROVED")
    
    # Recover crashed tasks
    recover_crashed_tasks()
    
    # Check states directly in DB
    from queue_engine.db import SessionLocal
    db = SessionLocal()
    task1 = db.query(QueueTask).filter(QueueTask.operation_id == op_id1).first()
    assert task1.status == "FAILED"
    
    task2 = db.query(QueueTask).filter(QueueTask.operation_id == op_id2).first()
    assert task2.status == "PROPOSED"
    db.close()

def test_snapshot_rollback_integrity(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")
    
    op_id = "test_op_123"
    metadata = create_snapshot(op_id, [str(test_file)])
    
    assert "archive_path" in metadata
    assert "hash" in metadata
    
    # Modify the file
    test_file.write_text("modified")
    
    # Mock an operation
    op = {"id": op_id, "module": "test", "rollback": {}}
    register_rollback(op, metadata)
    
    from core.engine import execute_rollback
    execute_rollback()
    
    assert test_file.read_text() == "hello world"

def test_snapshot_rollback_integrity_dict_targets(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world dict")
    
    op_id = "test_op_456"
    metadata = create_snapshot(op_id, [{"id": "test_id", "type": "file", "path": str(test_file)}])
    
    assert "archive_path" in metadata
    assert "hash" in metadata
    assert metadata["targets"] == [str(test_file)]
    
    # Modify the file
    test_file.write_text("modified dict")
    
    # Mock an operation
    op = {"id": op_id, "module": "test", "rollback": {}}
    register_rollback(op, metadata)
    
    from core.engine import execute_rollback
    execute_rollback()
    
    assert test_file.read_text() == "hello world dict"

def test_rollback_api_endpoint():
    from fastapi.testclient import TestClient
    from web.server import app
    from unittest.mock import patch
    
    client = TestClient(app)
    with patch("core.engine.execute_rollback") as mock_execute:
        response = client.post("/api/rollback/rb_test_123")
        assert response.status_code == 200
        assert response.json() == {"status": "success", "message": "Rollback rb_test_123 executed successfully"}
        mock_execute.assert_called_once_with("rb_test_123")
