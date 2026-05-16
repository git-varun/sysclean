"""Module docstring."""
import json
import pathlib


QUARANTINE_DIR = pathlib.Path(
    "runtime/quarantine"
)

QUARANTINE_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def quarantine(operation, reason):
    """Function docstring."""

    path = QUARANTINE_DIR / (
        f"{operation['id']}.json"
    )

    payload = {
        "operation": operation,
        "reason": reason
    }

    path.write_text(
        json.dumps(payload, indent=2)
    )
