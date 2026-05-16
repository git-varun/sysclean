"""Module docstring."""  # pylint: disable=too-few-public-methods
class AdaptivePolicyRuntime:
    """Class docstring."""

    def evolve(
        self,
        policy,
        telemetry
    ):
        """Function docstring."""

        if telemetry["cleanup_success_rate"] > 95:

            policy["autonomous_level"] = (
                "expanded"
            )

        return policy
