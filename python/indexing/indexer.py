"""Module docstring."""
from pathlib import Path


class SemanticIndexer:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def build_index(self, root):
        """Function docstring."""

        index = []

        for path in Path(root).rglob("*"):

            if path.is_file():

                index.append({
                    "path": str(path),
                    "extension": path.suffix,
                    "size_bytes": path.stat().st_size
                })

        return index
