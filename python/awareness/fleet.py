"""Module docstring."""  # pylint: disable=too-few-public-methods
class FleetIntelligence:
    """Class docstring."""

    def analyze(
        self,
        fleet
    ):
        """Function docstring."""

        return {
            "fleet_nodes":
                len(fleet),
            "average_disk_usage":
                sum(
                    x["disk_usage"]
                    for x in fleet
                ) / len(fleet)
        }
