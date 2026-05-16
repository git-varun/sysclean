"""Module docstring."""
class IncidentResponse:
    """Class docstring."""

    def classify(
        self,
        telemetry
    ):
        """Function docstring."""

        if telemetry["disk_usage"] > 95:

            return {
                "severity":
                    "critical",
                "incident":
                    "disk_exhaustion"
            }

        return {
            "severity":
                "normal"
        }

    def response_plan(
        self,
        incident
    ):
        """Function docstring."""

        return {
            "incident":
                incident,
            "actions": [
                "cleanup",
                "forecast",
                "snapshot"
            ]
        }
