import pytest
from unittest.mock import patch, MagicMock
import subprocess
from core.runtime import execute_operation, CommandExecutionError, CommandTimeoutError

@patch('core.runtime.validate_operation')
def test_execute_operation_security_validation_failure(mock_validate):
    mock_validate.side_effect = Exception("Validation failed")
    
    with pytest.raises(CommandExecutionError, match="Security validation failed"):
        execute_operation({"command": ["ls"]})

@patch('core.runtime.validate_operation')
@patch('core.runtime.emit_event')
@patch('core.runtime.create_snapshot')
@patch('core.runtime.register_rollback')
@patch('core.runtime.subprocess.run')
def test_execute_operation_success(mock_run, mock_register, mock_snapshot, mock_emit, mock_validate):
    mock_run.return_value = MagicMock(returncode=0, stderr="")
    mock_snapshot.return_value = {"snapshot": "meta"}
    
    op = {"id": "123", "command": ["echo", "test"], "targets": ["/tmp/test"]}
    execute_operation(op)
    
    mock_validate.assert_called_once_with(op)
    mock_snapshot.assert_called_once_with("123", ["/tmp/test"])
    mock_run.assert_called_once()
    mock_register.assert_called_once_with(op, {"snapshot": "meta"})

@patch('core.runtime.validate_operation')
@patch('core.runtime.emit_event')
@patch('core.runtime.subprocess.run')
def test_execute_operation_timeout(mock_run, mock_emit, mock_validate):
    mock_run.side_effect = subprocess.TimeoutExpired(cmd=["sleep", "10"], timeout=1)
    
    op = {"command": ["sleep", "10"], "timeout": 1}
    with pytest.raises(CommandTimeoutError, match="Command timed out"):
        execute_operation(op)

@patch('core.runtime.validate_operation')
@patch('core.runtime.emit_event')
@patch('core.runtime.subprocess.run')
def test_execute_operation_command_error(mock_run, mock_emit, mock_validate):
    mock_run.return_value = MagicMock(returncode=1, stderr="Error occurred")
    
    op = {"command": ["false"]}
    with pytest.raises(CommandExecutionError, match="Error occurred"):
        execute_operation(op)

@patch('core.runtime.validate_operation')
def test_execute_operation_invalid_command_type(mock_validate):
    with pytest.raises(ValueError, match="Command must be a list"):
        execute_operation({"command": "echo test"})
