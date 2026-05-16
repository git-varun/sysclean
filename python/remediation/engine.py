"""Module docstring."""  # pylint: disable=too-few-public-methods
class RemediationEngine:
    """Class docstring."""

    SAFE_ACTIONS = [
        "cache_cleanup",
        "log_cleanup",
        "docker_prune_safe"
    ]

    def execute(self, recommendation):
        """Function docstring."""

        action = recommendation["action"]

        if action not in self.SAFE_ACTIONS:
            raise RuntimeError(
                "Unsafe autonomous action"
            )

        return {
            "action": action,
            "status": "executed"
        }
