"""Module docstring."""  # pylint: disable=too-few-public-methods
class FederationAggregator:
    """Class docstring."""

    def aggregate(self, telemetry):
        """Function docstring."""

        fleet_storage = sum(
            node["storage_used_gb"]
            for node in telemetry
        )

        fleet_reclaim = sum(
            node["reclaimable_gb"]
            for node in telemetry
        )

        return {
            "fleet_storage_gb": fleet_storage,
            "fleet_reclaimable_gb": fleet_reclaim
        }
