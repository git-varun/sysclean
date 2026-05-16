"""Module docstring."""
import json
import pathlib
from datetime import datetime


EVENT_LOG = pathlib.Path(
    "runtime/events/events.jsonl"
)

EVENT_LOG.parent.mkdir(
    parents=True,
    exist_ok=True
)


def emit_event(event_type, payload):
    """Function docstring."""

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "payload": payload
    }

    with EVENT_LOG.open("a") as fh:  # pylint: disable=unspecified-encoding
        fh.write(json.dumps(entry) + "\n")
