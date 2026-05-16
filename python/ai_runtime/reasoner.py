"""Module docstring."""  # pylint: disable=too-few-public-methods
class TelemetryReasoner:
    """Class docstring."""

    def analyze(
        self,
        telemetry
    ):
        """Function docstring."""

        insights = []

        if telemetry["docker_growth"] > 25:

            insights.append({
                "severity": "high",
                "reason":
                    "Abnormal Docker growth detected"
            })

        return insights
