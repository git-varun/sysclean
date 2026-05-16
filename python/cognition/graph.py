"""Module docstring."""  # pylint: disable=too-few-public-methods
class CognitionGraph:
    """Class docstring."""

    def build(
        self,
        repos,
        containers,
        caches,
        incidents
    ):
        """Function docstring."""

        return {
            "nodes":
                len(repos)
                + len(containers)
                + len(caches),
            "incidents":
                len(incidents)
        }
