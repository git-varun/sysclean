"""Module docstring."""
import json
import socket
import sys

SOCKET_PATH = "/var/run/sysclean.sock"

def send_operation(operation, socket_path=SOCKET_PATH):
    """Function docstring."""
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client_sock:
        try:
            client_sock.connect(socket_path)
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
