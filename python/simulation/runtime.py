"""Module docstring."""  # pylint: disable=too-few-public-methods
class InfrastructureSimulation:
    """Class docstring."""

    def simulate_cleanup(
        self,
        telemetry,
        action
    ):
        """Function docstring."""

        projected = telemetry.copy()

        if action == "cache_cleanup":

            projected["disk_usage"] -= 10

        return projected
