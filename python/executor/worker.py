"""Module docstring."""
import json
import os
import socket
import threading
import time
from .runtime import execute_operation

SOCKET_PATH = "/var/run/sysclean.sock"

class DaemonListener:  # pylint: disable=too-few-public-methods
    """Class docstring."""
    def __init__(self, socket_path=SOCKET_PATH):
        self.socket_path = socket_path

    def start(self):
        """Function docstring."""
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_sock:
            server_sock.bind(self.socket_path)
            os.chmod(self.socket_path, 0o600)  # Restrict access
            server_sock.listen()
            print(f"Listening on {self.socket_path}...")

            while True:
                conn, _ = server_sock.accept()
                with conn:
                    data = conn.recv(4096)
                    if not data:
                        continue
                    try:
                        operation = json.loads(data.decode("utf-8"))
                        self._handle_operation(conn, operation)
                    except json.JSONDecodeError as exc:
                        self._send_response(conn, {"status": "error", "error": "Invalid JSON"})
                    except Exception as exc:  # pylint: disable=broad-exception-caught
                        self._send_response(conn, {"status": "error", "error": str(exc)})

    def _handle_operation(self, conn, operation):
        try:
            execute_operation(operation)
            self._send_response(conn, {"status": "success"})
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._send_response(conn, {"status": "error", "error": str(exc)})

    def _send_response(self, conn, response):
        conn.sendall(json.dumps(response).encode("utf-8"))

if __name__ == "__main__":
    listener = DaemonListener()
    listener.start()
