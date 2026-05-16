"""Module docstring."""  # pylint: disable=too-few-public-methods
class RecommendationExplainer:
    """Class docstring."""

    def explain(self, recommendation):
        """Function docstring."""

        return {
            "reason": recommendation["message"],
            "risk": recommendation.get("priority"),
            "rollback_available": True
        }
