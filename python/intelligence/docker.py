"""Module docstring."""
import subprocess


class DockerAnalyzer:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def docker_disk_usage(self):
        """Function docstring."""

        result = subprocess.run(
            ["docker", "system", "df", "--format", "json"],
            capture_output=True,
            text=True
        )

        return result.stdout
