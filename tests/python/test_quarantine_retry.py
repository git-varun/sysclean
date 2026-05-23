import pytest
import os
import tempfile
import pathlib
import json
from unittest.mock import patch

from core.quarantine import quarantine
import core.quarantine as quarantine_mod
from core.retry import retry_operation

def test_quarantine():
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = pathlib.Path(temp_dir)
        with patch.object(quarantine_mod, 'QUARANTINE_DIR', temp_path):
            operation = {"id": "op_test_123"}
            quarantine(operation, "Testing quarantine")
            
            file_path = temp_path / "op_test_123.json"
            assert file_path.exists()
            
            with open(file_path, "r") as f:
                data = json.load(f)
                
            assert data["operation"]["id"] == "op_test_123"
            assert data["reason"] == "Testing quarantine"

@patch('core.retry.time.sleep')
def test_retry_operation(mock_sleep):
    op = {"id": "op_1"}
    
    # Test valid retry counts
    assert retry_operation(op, 0) == True
    mock_sleep.assert_called_with(60)
    
    assert retry_operation(op, 1) == True
    mock_sleep.assert_called_with(300)
    
    assert retry_operation(op, 2) == True
    mock_sleep.assert_called_with(900)
    
    # Test exceeding retry limits
    assert retry_operation(op, 3) == False
    assert retry_operation(op, 10) == False
