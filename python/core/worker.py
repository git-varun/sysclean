"""Module docstring."""
import json
import os
import signal
import socket
import sys
import threading
import time

from queue_engine.db import SessionLocal
from queue_engine.models import QueueTask
from queue_engine.queue import enqueue, recover_crashed_tasks, transition_state, recover_stale_tasks
from core.runtime import execute_operation

SOCKET_PATH = "/var/run/sysclean.sock"


class QueueProcessor(threading.Thread):
    """Background worker to process operations from the database queue."""
    def __init__(self):
        super().__init__(daemon=True)
        self._running = True

    def run(self):
        last_recover_time = time.time()
        while self._running:
            # Recover stale tasks every 5 minutes
            if time.time() - last_recover_time > 300:
                recover_stale_tasks()
                last_recover_time = time.time()

            db = SessionLocal()
            try:
                task = db.query(QueueTask).filter(
                    QueueTask.status.in_(["PROPOSED", "APPROVED"])
                ).first()

                if task:
                    op_id = task.operation_id
                    payload = task.payload_json
                    current_status = task.status
                    db.close()

                    if current_status == "PROPOSED":
                        if not transition_state(op_id, "APPROVED", "PROPOSED"):
                            continue
                        current_status = "APPROVED"

                    if current_status == "APPROVED":
                        if not transition_state(op_id, "EXECUTING", "APPROVED"):
                            continue

                    try:
                        execute_operation(payload)
                        transition_state(op_id, "COMPLETED", "EXECUTING")
                    except Exception:  # pylint: disable=broad-exception-caught
                        transition_state(op_id, "FAILED", "EXECUTING")
                else:
                    db.close()
                    time.sleep(1.0)
            except Exception:  # pylint: disable=broad-exception-caught
                pass
            finally:
                db.close()

    def stop(self):
        """Function docstring."""
        self._running = False


class DaemonListener:  # pylint: disable=too-few-public-methods
    """Class docstring."""
    def __init__(self, socket_path=SOCKET_PATH):
        self.socket_path = socket_path
        self._running = True
        self.processor = QueueProcessor()

    def _shutdown(self, _signum, _frame):
        print("Shutting down syscleand...")
        self._running = False
        self.processor.stop()
        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except FileNotFoundError:
                pass
        sys.exit(0)

    def start(self):
        """Function docstring."""
        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        # Recover crashed tasks before starting listening
        recover_crashed_tasks()

        # Start the background queue processor
        self.processor.start()

        if os.path.exists(self.socket_path):
            try:
                os.remove(self.socket_path)
            except FileNotFoundError:
                pass

        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_sock:
            server_sock.bind(self.socket_path)
            os.chmod(self.socket_path, 0o600)  # Restrict access
            server_sock.listen()
            print(f"Listening on {self.socket_path}...")

            # Use a timeout so we can periodically check self._running
            server_sock.settimeout(1.0)

            while self._running:
                try:
                    conn, _ = server_sock.accept()
                    with conn:
                        data = conn.recv(4096)
                        if not data:
                            continue
                        try:
                            operation = json.loads(data.decode("utf-8"))
                            self._handle_operation(conn, operation)
                        except json.JSONDecodeError:
                            self._send_response(conn, {"status": "error", "error": "Invalid JSON"})
                        except Exception as exc:  # pylint: disable=broad-exception-caught
                            self._send_response(conn, {"status": "error", "error": str(exc)})
                except socket.timeout:
                    continue

    def _handle_operation(self, conn, operation):
        try:
            # Instead of executing synchronously, we push to the queue
            module = operation.get("module", "unknown")
            risk_level = operation.get("risk_level", "safe")
            operation_id = enqueue(module, operation, risk_level)
            self._send_response(conn, {"status": "success", "operation_id": operation_id})
        except Exception as exc:  # pylint: disable=broad-exception-caught
            self._send_response(conn, {"status": "error", "error": str(exc)})

    def _send_response(self, conn, response):
        conn.sendall(json.dumps(response).encode("utf-8"))

if __name__ == "__main__":
    listener = DaemonListener()
    listener.start()
