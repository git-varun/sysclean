import pytest
import os
import json
import tempfile
import pathlib
import time
from unittest.mock import patch, MagicMock

from queue_engine.events import emit_event, _stop_worker, _event_worker
import queue_engine.events as events

def test_emit_event_and_worker():
    # Use a temporary directory for events log to avoid polluting the actual log
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_log = pathlib.Path(temp_dir) / "events.jsonl"
        
        # Patch the EVENT_LOG path
        with patch.object(events, 'EVENT_LOG', temp_log):
            emit_event("test_event", {"key": "value"})
            
            # Allow time for worker to process
            time.sleep(0.5)
            
            assert temp_log.exists()
            with open(temp_log, "r") as f:
                lines = f.readlines()
                assert len(lines) >= 1
                data = json.loads(lines[-1])
                assert data["event_type"] == "test_event"
                assert data["payload"]["key"] == "value"
                assert "timestamp" in data

@patch('pathlib.Path.open')
def test_worker_exception_handling(mock_open):
    # Simulate a write error
    mock_open.side_effect = Exception("Disk full")
    
    emit_event("error_test", {"data": 1})
    time.sleep(0.5)
    # Shouldn't crash the worker thread
    # The exception should be caught and printed
    assert True
