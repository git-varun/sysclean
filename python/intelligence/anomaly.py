"""Module docstring."""
import statistics


class AnomalyDetector:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def detect_growth_spike(self, values):
        """Function docstring."""

        if len(values) < 5:
            return False

        mean = statistics.mean(values[:-1])
        latest = values[-1]

        return latest > mean * 2
