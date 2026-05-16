"""Module docstring."""  # pylint: disable=too-few-public-methods
class SelfOptimizingScheduler:
    """Class docstring."""

    def optimize(
        self,
        historical_runs
    ):
        """Function docstring."""

        best_window = min(
            historical_runs,
            key=lambda x: x["cpu_load"]
        )

        return {
            "recommended_window":
                best_window
        }
