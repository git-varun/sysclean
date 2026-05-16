"""Module docstring."""
class OrchestrationController:
    """Class docstring."""

    def __init__(self):
        self.nodes = []

    def register_node(self, node):
        """Function docstring."""
        self.nodes.append(node)

    def broadcast(self, task):
        """Function docstring."""

        results = []

        for node in self.nodes:
            results.append(
                node.execute(task)
            )

        return results
