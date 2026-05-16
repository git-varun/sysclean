"""Module docstring."""  # pylint: disable=too-few-public-methods
class PredictiveMemory:
    """Class docstring."""

    def future_state(
        self,
        telemetry
    ):
        """Function docstring."""

        return {
            "future_disk_usage":
                telemetry["disk_usage"] + 12
        }
