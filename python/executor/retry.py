"""Module docstring."""
import time


RETRY_DELAYS = [
    60,
    300,
    900
]


def retry_operation(operation, retry_count):
    _ = operation
    """Function docstring."""

    if retry_count >= len(RETRY_DELAYS):
        return False

    delay = RETRY_DELAYS[retry_count]

    time.sleep(delay)

    return True
