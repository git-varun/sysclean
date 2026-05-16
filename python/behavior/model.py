"""Module docstring."""  # pylint: disable=too-few-public-methods
class BehavioralModel:
    """Class docstring."""

    def profile(
        self,
        telemetry_history
    ):
        """Function docstring."""

        average_growth = sum(
            telemetry_history
        ) / len(telemetry_history)

        return {
            "average_growth":
                average_growth
        }
