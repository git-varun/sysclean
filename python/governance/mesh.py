"""Module docstring."""  # pylint: disable=too-few-public-methods
class MeshGovernance:
    """Class docstring."""

    def authorize(
        self,
        action
    ):
        """Function docstring."""

        if action["risk"] > 50:

            return False

        return True
