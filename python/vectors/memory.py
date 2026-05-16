"""Module docstring."""
import numpy as np


class VectorMemory:
    """Class docstring."""

    def __init__(self):

        self.memory = []

    def store(
        self,
        embedding,
        metadata
    ):
        """Function docstring."""

        self.memory.append({
            "embedding": embedding,
            "metadata": metadata
        })

    def search(
        self,
        query_embedding
    ):
        """Function docstring."""

        similarities = []

        for item in self.memory:

            similarity = np.dot(
                item["embedding"],
                query_embedding
            )

            similarities.append({
                "similarity": similarity,
                "metadata": item["metadata"]
            })

        return sorted(
            similarities,
            key=lambda x: x["similarity"],
            reverse=True
        )
