"""Module docstring."""  # pylint: disable=too-few-public-methods
class ReputationEngine:
    """Class docstring."""

    def score(self, metadata):
        """Function docstring."""

        score = 100

        if metadata.get("unmaintained"):
            score -= 40

        if metadata.get("deprecated"):
            score -= 30

        return max(score, 0)
