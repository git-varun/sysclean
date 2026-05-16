"""Module docstring."""  # pylint: disable=too-few-public-methods
class AutonomousRiskEngine:
    """Class docstring."""

    def evaluate(
        self,
        telemetry
    ):
        """Function docstring."""

        score = 0

        if telemetry["disk_usage"] > 90:
            score += 30

        if telemetry["docker_growth"] > 20:
            score += 20

        return {
            "risk_score": score
        }
