"""Module docstring."""  # pylint: disable=too-few-public-methods
class RemediationGenerator:
    """Class docstring."""

    def generate(
        self,
        incident
    ):
        """Function docstring."""
        _ = incident

        return {
            "script":
                "docker system prune -f",
            "risk":
                "medium"
        }
