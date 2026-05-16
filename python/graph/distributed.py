"""Module docstring."""  # pylint: disable=too-few-public-methods
class DistributedGraphAnalytics:
    """Class docstring."""

    def correlate(
        self,
        graphs
    ):
        """Function docstring."""

        merged_nodes = 0

        for graph in graphs:
            merged_nodes += len(graph)

        return {
            "total_nodes": merged_nodes
        }
