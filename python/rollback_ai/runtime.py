"""Module docstring."""  # pylint: disable=too-few-public-methods
class RollbackAI:
    """Class docstring."""

    def choose(
        self,
        rollback_candidates
    ):
        """Function docstring."""

        safest = min(
            rollback_candidates,
            key=lambda x: x["risk"]
        )

        return safest
