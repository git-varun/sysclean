import pytest
import os
import json
import threading
import time
from unittest.mock import patch, MagicMock
from core.worker import QueueProcessor, DaemonListener

@patch('core.worker.SessionLocal')
@patch('core.worker.recover_stale_tasks')
@patch('core.worker.transition_state')
@patch('core.worker.execute_operation')
def test_queue_processor(mock_execute, mock_transition, mock_recover, mock_session):
    # Mock DB task
    mock_db = MagicMock()
    mock_session.return_value = mock_db
    
    mock_task = MagicMock()
    mock_task.operation_id = "op1"
    mock_task.payload_json = {"command": ["echo"]}
    mock_task.status = "PROPOSED"
    
    # Return a task on the first query, then None
    mock_query = mock_db.query().filter().first
    mock_query.side_effect = [mock_task, None, None]
    
    mock_transition.return_value = True
    
    processor = QueueProcessor()
    
    # Run it briefly in a thread to process the task, then stop
    thread = threading.Thread(target=processor.run)
    thread.daemon = True
    thread.start()
    
    time.sleep(0.1)
    processor.stop()
    thread.join(timeout=1.0)
    
    mock_transition.assert_any_call("op1", "APPROVED", "PROPOSED")
    mock_transition.assert_any_call("op1", "EXECUTING", "APPROVED")
    mock_execute.assert_called_once_with({"command": ["echo"]})
    mock_transition.assert_any_call("op1", "COMPLETED", "EXECUTING")

@patch('core.worker.os.remove')
@patch('core.worker.os.chmod')
@patch('core.worker.socket.socket')
@patch('core.worker.recover_crashed_tasks')
@patch('core.worker.enqueue')
def test_daemon_listener(mock_enqueue, mock_recover, mock_socket, mock_chmod, mock_remove):
    mock_server = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_server
    
    # Mock a connection with a JSON payload
    mock_conn = MagicMock()
    mock_conn.recv.side_effect = [
        json.dumps({"module": "test", "risk_level": "safe"}).encode('utf-8'),
        b""
    ]
    
    mock_server.accept.side_effect = [(mock_conn, ("test", 0)), Exception("Stop")]
    
    mock_enqueue.return_value = "op123"
    
    listener = DaemonListener(socket_path="/tmp/test.sock")
    listener.processor = MagicMock() # Mock the background processor to avoid starting it
    
    try:
        listener.start()
    except Exception as e:
        if str(e) != "Stop":
            raise
    
    mock_enqueue.assert_called_once_with("test", {"module": "test", "risk_level": "safe"}, "safe")
    
    # Ensure success response sent
    expected_resp = json.dumps({"status": "success", "operation_id": "op123"}).encode("utf-8")
    mock_conn.sendall.assert_called_once_with(expected_resp)
