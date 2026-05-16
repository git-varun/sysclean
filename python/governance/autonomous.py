"""Module docstring."""  # pylint: disable=too-few-public-methods
class AutonomousGovernance:
    """Class docstring."""

    MAX_AUTONOMOUS_RISK = 35

    def approve(self, plan):
        """Function docstring."""

        if (
            plan["risk_score"]
            > self.MAX_AUTONOMOUS_RISK
        ):
            return False

        return True
