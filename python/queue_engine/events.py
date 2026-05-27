"""Module docstring."""
import json
import pathlib
import threading
import collections
import atexit
from datetime import datetime, timezone


EVENT_LOG = pathlib.Path.home() / ".local/share/sysclean/events.jsonl"

EVENT_LOG.parent.mkdir(
    parents=True,
    exist_ok=True
)

_event_queue = collections.deque()
_event_cond = threading.Condition()
_running = True

def _event_worker():
    while True:
        with _event_cond:
            while not _event_queue and _running:
                _event_cond.wait(timeout=1.0)

            if not _event_queue and not _running:
                break

            if _event_queue:
                entry = _event_queue.popleft()
            else:
                continue

        try:
            with EVENT_LOG.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry) + "\n")
        except Exception as exc:  # pylint: disable=broad-exception-caught
            print(f"Failed to write event log: {exc}")

_worker_thread = threading.Thread(target=_event_worker, daemon=True)
_worker_thread.start()

def _stop_worker():
    global _running  # pylint: disable=global-statement
    with _event_cond:
        _running = False
        _event_cond.notify_all()
    _worker_thread.join(timeout=2.0)

atexit.register(_stop_worker)

def emit_event(event_type, payload):
    """Function docstring."""

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "payload": payload
    }

    with _event_cond:
        _event_queue.append(entry)
        _event_cond.notify()
