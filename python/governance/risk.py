"""Module docstring."""  # pylint: disable=too-few-public-methods
class GovernanceEngine:
    """Class docstring."""

    MAX_RISK = 75

    def validate(self, plan):
        """Function docstring."""

        if plan["risk_score"] > self.MAX_RISK:
            raise RuntimeError(
                "Plan exceeds governance threshold"
            )
