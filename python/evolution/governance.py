"""Module docstring."""  # pylint: disable=too-few-public-methods
class EvolvingGovernance:
    """Class docstring."""

    def evolve(
        self,
        governance,
        telemetry
    ):
        """Function docstring."""

        if telemetry[
            "cleanup_success_rate"
        ] > 98:

            governance[
                "autonomous_threshold"
            ] += 5

        return governance
