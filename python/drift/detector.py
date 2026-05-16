"""Module docstring."""  # pylint: disable=too-few-public-methods
class DriftDetector:
    """Class docstring."""

    def detect(
        self,
        baseline,
        current
    ):
        """Function docstring."""

        drift = []

        for key, value in current.items():

            if baseline.get(key) != value:

                drift.append({
                    "field": key,
                    "baseline":
                        baseline.get(key),
                    "current": value
                })

        return drift
