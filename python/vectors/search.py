"""Module docstring."""  # pylint: disable=too-few-public-methods
class SemanticSearch:
    """Class docstring."""

    def query(
        self,
        index,
        query
    ):
        """Function docstring."""
        _ = query

        return sorted(
            index,
            key=lambda x:
                x["score"],
            reverse=True
        )
