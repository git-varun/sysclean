"""Module docstring."""
from datetime import datetime


class AutonomousScheduler:
    """Class docstring."""

    def should_run_cleanup(
        self,
        disk_usage,
        reclaimable_gb
    ):
        """Function docstring."""

        if disk_usage > 85:
            return True

        if reclaimable_gb > 20:
            return True

        return False

    def next_window(self):
        """Function docstring."""

        return datetime.utcnow().isoformat()
