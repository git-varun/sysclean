"""Module docstring."""
class MeshRuntime:
    """Class docstring."""

    def __init__(self):

        self.nodes = {}

    def register(
        self,
        node_id,
        metadata
    ):
        """Function docstring."""

        self.nodes[node_id] = metadata

    def dispatch(
        self,
        task
    ):
        """Function docstring."""

        results = []

        for node in self.nodes.values():

            results.append({
                "node": node,
                "task": task,
                "status": "scheduled"
            })

        return results
