"""Module docstring."""
from pathlib import Path


class RepoAnalyzer:
    """Class docstring."""

    def discover_repositories(self, root):
        """Function docstring."""

        repositories = []

        for path in Path(root).rglob(".git"):
            repositories.append(path.parent)

        return repositories

    def analyze_repository(self, repo_path):
        """Function docstring."""

        git_size = sum(
            f.stat().st_size
            for f in Path(repo_path).rglob("*")
            if f.is_file()
        )

        return {
            "repo": str(repo_path),
            "size_mb": round(git_size / 1024 / 1024, 2)
        }
