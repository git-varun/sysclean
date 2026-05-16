"""Module docstring."""
from datetime import datetime, timedelta


class ForecastEngine:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def estimate_disk_exhaustion(
        self,
        used_gb,
        daily_growth_gb,
        total_gb
    ):
        """Function docstring."""

        remaining = total_gb - used_gb

        if daily_growth_gb <= 0:
            return None

        days = remaining / daily_growth_gb

        return {
            "estimated_days_remaining": round(days, 2),
            "estimated_exhaustion_date": (
                datetime.utcnow() + timedelta(days=days)
            ).isoformat()
        }
