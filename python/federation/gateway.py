"""Module docstring."""  # pylint: disable=too-few-public-methods
class TelemetryGateway:
    """Class docstring."""

    def publish(
        self,
        telemetry
    ):
        """Function docstring."""

        return {
            "published": True,
            "records": len(telemetry)
        }
