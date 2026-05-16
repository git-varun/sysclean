"""Module docstring."""  # pylint: disable=too-few-public-methods
class SemanticStorageIntelligence:
    """Class docstring."""

    def classify(
        self,
        path,
        metadata
    ):
        """Function docstring."""
        _ = path

        if metadata["size_gb"] > 20:

            return {
                "classification":
                    "high-value-storage"
            }

        return {
            "classification":
                "standard"
        }
