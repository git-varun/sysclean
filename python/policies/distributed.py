"""Module docstring."""  # pylint: disable=too-few-public-methods
class DistributedPolicyRuntime:
    """Class docstring."""

    def evaluate(
        self,
        fleet_state
    ):
        """Function docstring."""

        violations = []

        for node in fleet_state:

            if node["disk_usage"] > 90:
                violations.append(node)

        return violations
