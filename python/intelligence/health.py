"""Module docstring."""
from dataclasses import dataclass


@dataclass
class HealthReport:
    """Class docstring."""
    score: int
    storage_pressure: float
    cache_bloat: float
    docker_bloat: float
    repo_entropy: float


class HealthScorer:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def calculate(
        self,
        storage_pressure,
        cache_bloat,
        docker_bloat,
        repo_entropy
    ):
        """Function docstring."""

        penalties = (
            storage_pressure * 0.35 +
            cache_bloat * 0.20 +
            docker_bloat * 0.25 +
            repo_entropy * 0.20
        )

        score = max(0, 100 - int(penalties))

        return HealthReport(
            score=score,
            storage_pressure=storage_pressure,
            cache_bloat=cache_bloat,
            docker_bloat=docker_bloat,
            repo_entropy=repo_entropy
        )
