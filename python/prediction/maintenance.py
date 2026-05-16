"""Module docstring."""  # pylint: disable=too-few-public-methods
class PredictiveMaintenance:
    """Class docstring."""

    def predict_failure(
        self,
        telemetry
    ):
        """Function docstring."""

        if telemetry["disk_usage"] > 95:

            return {
                "risk": "critical",
                "prediction":
                    "Disk exhaustion imminent"
            }

        return {
            "risk": "low"
        }
