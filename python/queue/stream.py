"""Module docstring."""
import psutil


def current_metrics():
    """Function docstring."""

    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "swap_percent": psutil.swap_memory().percent
    }
