"""Module docstring."""
import random


class CleanupRLAgent:
    """Class docstring."""

    ACTIONS = [
        "cache_cleanup",
        "docker_cleanup",
        "log_cleanup"
    ]

    def choose_action(self):
        """Function docstring."""

        return random.choice(
            self.ACTIONS
        )

    def reward(
        self,
        reclaimed_gb,
        risk_score
    ):
        """Function docstring."""

        return (
            reclaimed_gb * 10
            - risk_score
        )
