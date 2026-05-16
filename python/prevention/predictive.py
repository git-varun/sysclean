"""Module docstring."""  # pylint: disable=too-few-public-methods
class PredictiveCleanup:
    """Class docstring."""

    def next_cleanup(
        self,
        telemetry
    ):
        """Function docstring."""

        if telemetry["growth_velocity"] > 5:

            return {
                "cleanup_window":
                    "within_24_hours"
            }

        return {
            "cleanup_window":
                "normal"
        }
