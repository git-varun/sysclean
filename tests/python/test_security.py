import pytest
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from security.validation import is_path_safe, validate_operation
from security.secrets import contains_secret
from security.classifier import is_protected
from security.cve import CVEEngine
from security.reputation import ReputationEngine

def test_is_path_safe():
    assert is_path_safe("/tmp/test_dir/file.txt") == True
    assert is_path_safe("/tmp/test_dir/.env") == False
    assert is_path_safe("/opt/app/wallet.dat") == False
    ssh_path = str(Path.home() / ".ssh" / "id_rsa")
    assert is_path_safe(ssh_path) == False
    traversal_path = str(Path.home() / "Documents" / ".." / ".ssh" / "config")
    assert is_path_safe(traversal_path) == False

def test_validate_operation():
    op_safe = {
        "risk_level": "safe",
        "targets": ["/tmp/safe_file.txt"]
    }
    assert validate_operation(op_safe) == True
    
    # Test dictionary target formatting
    op_safe_dict = {
        "risk_level": "safe",
        "targets": [{"id": "test_id", "type": "directory", "path": "/tmp/safe_file.txt"}]
    }
    assert validate_operation(op_safe_dict) == True
    
    op_unsafe_dict = {
        "risk_level": "safe",
        "targets": [{"id": "test_id", "type": "file", "path": str(Path.home() / ".ssh" / "id_rsa")}]
    }
    with pytest.raises(PermissionError):
        validate_operation(op_unsafe_dict)
        
    op_unsafe_target = {
        "risk_level": "safe",
        "targets": ["/tmp/safe_file.txt", str(Path.home() / ".ssh" / "id_rsa")]
    }
    with pytest.raises(PermissionError):
        validate_operation(op_unsafe_target)
        
    op_unsafe_tier = {
        "risk_level": "unknown_tier",
        "targets": ["/tmp/safe_file.txt"]
    }
    with pytest.raises(ValueError):
        validate_operation(op_unsafe_tier)

def test_contains_secret():
    assert contains_secret("This is a BEGIN RSA PRIVATE KEY") == True
    assert contains_secret("my api_key=123") == True
    assert contains_secret("just a normal string") == False

def test_is_protected():
    assert is_protected("/path/to/.env") == True
    assert is_protected("/path/to/keystore/file") == True
    assert is_protected("/safe/path/file.txt") == False

@patch('security.cve.requests.post')
def test_cve_engine(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"vulns": []}
    mock_post.return_value = mock_response
    
    engine = CVEEngine()
    result = engine.query_package("curl")
    
    assert result == {"vulns": []}
    mock_post.assert_called_once_with(
        "https://api.osv.dev/v1/query",
        json={"package": {"name": "curl"}},
        timeout=10
    )

def test_reputation_engine():
    engine = ReputationEngine()
    assert engine.score({}) == 100
    assert engine.score({"unmaintained": True}) == 60
    assert engine.score({"deprecated": True}) == 70
    assert engine.score({"unmaintained": True, "deprecated": True}) == 30
