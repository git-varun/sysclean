"""Module docstring."""  # pylint: disable=too-few-public-methods
class AwarenessGraph:
    """Class docstring."""

    def correlate(
        self,
        telemetry,
        incidents
    ):
        """Function docstring."""
        _ = telemetry

        return {
            "incident_links":
                len(incidents),
            "risk_state":
                "elevated"
        }
