"""Module docstring."""  # pylint: disable=too-few-public-methods
class DistributedRemediation:
    """Class docstring."""

    def build_plan(
        self,
        fleet_state
    ):
        """Function docstring."""

        plan = []

        for node in fleet_state:

            if node["disk_usage"] > 90:

                plan.append({
                    "node": node["id"],
                    "action":
                        "cache_cleanup"
                })

        return plan
