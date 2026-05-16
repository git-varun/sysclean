"""Module docstring."""
class DigitalTwin:
    """Class docstring."""

    def snapshot(
        self,
        telemetry,
        packages,
        repos
    ):
        """Function docstring."""

        return {
            "telemetry": telemetry,
            "packages": packages,
            "repos": repos
        }

    def compare(
        self,
        old,
        new
    ):
        """Function docstring."""

        return {
            "changes":
                len(new.keys())
                - len(old.keys())
        }
