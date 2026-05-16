"""Module docstring."""
from fastapi import WebSocket


async def telemetry_socket(ws: WebSocket):
    """Function docstring."""

    await ws.accept()

    while True:
        await ws.send_json({
            "type": "telemetry",
            "status": "running"
        })
