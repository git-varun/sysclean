"""Module docstring."""
import networkx as nx


class ResourceGraph:
    """Class docstring."""

    def __init__(self):

        self.graph = nx.Graph()

    def add_relationship(
        self,
        source,
        target,
        relation
    ):
        """Function docstring."""

        self.graph.add_edge(
            source,
            target,
            relation=relation
        )

    def dependencies(self, node):
        """Function docstring."""

        return list(
            self.graph.neighbors(node)
        )
