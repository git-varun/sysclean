"""Module docstring."""  # pylint: disable=too-few-public-methods
class KnowledgeGraph:
    """Class docstring."""

    def correlate(
        self,
        repo,
        node_modules,
        docker_volumes
    ):
        """Function docstring."""

        return {
            "repo": repo,
            "related_node_modules":
                node_modules,
            "related_volumes":
                docker_volumes
        }
