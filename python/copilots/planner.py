"""Module docstring."""  # pylint: disable=too-few-public-methods
class CleanupPlanner:
    """Class docstring."""

    def generate(
        self,
        telemetry
    ):
        """Function docstring."""
        _ = telemetry

        return {
            "steps": [
                "docker_cleanup",
                "cache_cleanup",
                "journal_cleanup"
            ]
        }
