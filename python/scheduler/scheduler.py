"""Module docstring."""
from resources import current_resources


def recommended_workers():
    """Function docstring."""

    metrics = current_resources()

    if metrics["cpu_percent"] > 80:
        return 1

    if metrics["memory_percent"] > 85:
        return 1

    return 4
