"""Module docstring."""  # pylint: disable=too-few-public-methods
class GovernanceConsensus:
    """Class docstring."""

    def authorize(
        self,
        action,
        governance
    ):
        """Function docstring."""

        return (
            action["risk"]
            <= governance["max_risk"]
        )
