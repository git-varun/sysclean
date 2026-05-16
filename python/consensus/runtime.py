"""Module docstring."""  # pylint: disable=too-few-public-methods
class ConsensusRuntime:
    """Class docstring."""

    def vote(
        self,
        nodes,
        proposal
    ):
        """Function docstring."""
        _ = proposal

        approvals = 0

        for node in nodes:

            if node["healthy"]:
                approvals += 1

        return approvals > (
            len(nodes) // 2
        )
