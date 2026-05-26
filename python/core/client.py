"""Client for communicating with the SysClean daemon."""
import json
import socket
import sys
import pathlib
import subprocess
import time
import os

SOCKET_PATH = str(pathlib.Path.home() / ".local/share/sysclean/sysclean.sock")

def spawn_daemon():
    """Spawn the sysclean daemon in the background."""
    print("Daemon not found. Auto-starting syscleand...", file=sys.stderr)
    worker_script = pathlib.Path(__file__).parent / "worker.py"
    
    subprocess.Popen(
        [sys.executable, str(worker_script)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    # Give the daemon time to start up and bind the socket
    time.sleep(1.5)

def send_operation(operation, socket_path=SOCKET_PATH, retry=True):
    """Sends an operation to the daemon queue."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_sock:
        client_sock.settimeout(10.0)
        try:
            client_sock.connect(socket_path)
        except (FileNotFoundError, ConnectionRefusedError):
            if retry:
                spawn_daemon()
                return send_operation(operation, socket_path, retry=False)
            else:
                print("Failed to connect to daemon after auto-starting.", file=sys.stderr)
                sys.exit(1)
        except socket.timeout:
            print("Request to daemon timed out", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Failed to communicate with daemon: {exc}", file=sys.stderr)
            sys.exit(1)

        try:
            client_sock.sendall(json.dumps(operation).encode("utf-8"))
            response_data = client_sock.recv(4096)
            if response_data:
                response = json.loads(response_data.decode("utf-8"))
                if response.get("status") != "success":
                    print(f"Error from daemon: {response.get('error')}", file=sys.stderr)
                    sys.exit(1)
            else:
                print("No response from daemon", file=sys.stderr)
                sys.exit(1)
        except socket.timeout:
            print("Request to daemon timed out", file=sys.stderr)
            sys.exit(1)
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Failed to communicate with daemon: {exc}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: client.py <operation_json>", file=sys.stderr)
        sys.exit(1)

    try:
        operation = json.loads(sys.argv[1])
        send_operation(operation)
    except json.JSONDecodeError:
        print("Invalid JSON operation", file=sys.stderr)
        sys.exit(1)
