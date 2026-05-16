"""Module docstring."""
from fastapi import WebSocket


class FleetStream:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    async def stream(
        self,
        ws: WebSocket
    ):
        """Function docstring."""

        await ws.accept()

        while True:

            await ws.send_json({
                "fleet_status": "healthy"
            })
