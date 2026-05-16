"""Module docstring."""
from pathlib import Path


IDE_CACHE_PATHS = [
    ".cache/JetBrains",
    ".config/Code/Cache",
    ".cache/Cursor"
]


class IDEAnalyzer:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def analyze(self, home):
        """Function docstring."""

        report = []

        for relative in IDE_CACHE_PATHS:

            path = Path(home) / relative

            if path.exists():
                report.append({
                    "path": str(path),
                    "size_mb": round(
                        sum(
                            f.stat().st_size
                            for f in path.rglob("*")
                            if f.is_file()
                        ) / 1024 / 1024,
                        2
                    )
                })

        return report
