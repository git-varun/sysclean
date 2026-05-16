"""Module docstring."""
from pathlib import Path


SEMANTIC_PATTERNS = {
    "dataset": ["csv", "parquet"],
    "model": ["gguf", "safetensors"],
    "archive": ["zip", "tar", "7z"],
    "media": ["mp4", "mkv"]
}


class SemanticClassifier:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def classify(self, path):
        """Function docstring."""

        suffix = Path(path).suffix.replace(".", "")

        for category, patterns in SEMANTIC_PATTERNS.items():

            if suffix in patterns:
                return category

        return "unknown"
