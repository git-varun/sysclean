"""Module docstring."""  # pylint: disable=too-few-public-methods
class RecommendationEngine:
    """Class docstring."""

    def generate(self, telemetry):
        """Function docstring."""

        recommendations = []

        if telemetry["docker_unused_gb"] > 20:
            recommendations.append({
                "priority": "high",
                "message": "Large unused Docker storage detected"
            })

        if telemetry["cache_growth_gb"] > 10:
            recommendations.append({
                "priority": "medium",
                "message": "Aggressive cache growth detected"
            })

        return recommendations
