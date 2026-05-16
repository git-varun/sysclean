"""Module docstring."""
from abc import ABC, abstractmethod


class AIProvider(ABC):  # pylint: disable=too-few-public-methods
    """Class docstring."""

    @abstractmethod
    def generate_recommendation(self, telemetry):
        """Function docstring."""
        pass
