"""Module docstring."""  # pylint: disable=too-few-public-methods
class FleetPropagation:
    """Class docstring."""

    def propagate(
        self,
        anomaly,
        fleet
    ):
        """Function docstring."""

        affected = []

        for node in fleet:

            if node["profile"] == anomaly["profile"]:

                affected.append(node)

        return affected
