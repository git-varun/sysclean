"""Module docstring."""
from sentence_transformers import SentenceTransformer


class EmbeddingRuntime:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def embed(
        self,
        text
    ):
        """Function docstring."""

        return self.model.encode(text)
