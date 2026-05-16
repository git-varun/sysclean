"""Module docstring."""  # pylint: disable=too-few-public-methods
class IncidentPrevention:
    """Class docstring."""

    def prevent(
        self,
        telemetry
    ):
        """Function docstring."""

        if telemetry["disk_growth"] > 15:

            return {
                "preventive_action":
                    "cache_cleanup"
            }

        return {
            "preventive_action":
                None
        }
