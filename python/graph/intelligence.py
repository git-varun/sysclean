"""Module docstring."""  # pylint: disable=too-few-public-methods
class GraphIntelligence:
    """Class docstring."""

    def detect_orphans(
        self,
        graph
    ):
        """Function docstring."""

        return [
            node
            for node in graph.nodes
            if graph.degree(node) == 0
        ]
