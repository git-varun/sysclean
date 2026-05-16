"""Module docstring."""  # pylint: disable=too-few-public-methods
class AutonomousLoop:
    """Class docstring."""

    def execute(
        self,
        telemetry
    ):
        """Function docstring."""

        if telemetry["disk_usage"] > 90:

            return {
                "action":
                    "autonomous_cleanup",
                "status":
                    "scheduled"
            }

        return {
            "status":
                "stable"
        }
