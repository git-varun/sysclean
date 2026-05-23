import pytest
import json
import socket
import sys
from unittest.mock import patch, MagicMock
from core.client import send_operation

@patch('core.client.socket.socket')
def test_send_operation_success(mock_socket):
    mock_conn = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    
    mock_conn.recv.return_value = json.dumps({"status": "success", "operation_id": "op_123"}).encode('utf-8')
    
    # Should not raise SystemExit
    send_operation({"test": "data"}, socket_path="/tmp/test.sock")
    
    mock_conn.sendall.assert_called_once()
    sent_data = json.loads(mock_conn.sendall.call_args[0][0].decode('utf-8'))
    assert sent_data == {"test": "data"}

@patch('core.client.socket.socket')
@patch('core.client.sys.exit')
def test_send_operation_connection_error(mock_exit, mock_socket):
    mock_conn = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    mock_conn.connect.side_effect = Exception("Socket missing")
    
    send_operation({"test": "data"}, socket_path="/tmp/test.sock")
    mock_exit.assert_called_once_with(1)

@patch('core.client.socket.socket')
@patch('core.client.sys.exit')
def test_send_operation_timeout(mock_exit, mock_socket):
    mock_conn = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    mock_conn.connect.side_effect = socket.timeout()
    
    send_operation({"test": "data"}, socket_path="/tmp/test.sock")
    mock_exit.assert_called_once_with(1)

@patch('core.client.socket.socket')
@patch('core.client.sys.exit')
def test_send_operation_no_response(mock_exit, mock_socket):
    mock_conn = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    mock_conn.recv.return_value = b""
    
    send_operation({"test": "data"}, socket_path="/tmp/test.sock")
    mock_exit.assert_called_once_with(1)

@patch('core.client.socket.socket')
@patch('core.client.sys.exit')
def test_send_operation_error_response(mock_exit, mock_socket):
    mock_conn = MagicMock()
    mock_socket.return_value.__enter__.return_value = mock_conn
    mock_conn.recv.return_value = json.dumps({"status": "error", "error": "Invalid params"}).encode('utf-8')
    
    send_operation({"test": "data"}, socket_path="/tmp/test.sock")
    mock_exit.assert_called_once_with(1)
