"""Module docstring."""
import requests
import logging  # pylint: disable=wrong-import-order

from providers.base import AIProvider

logger = logging.getLogger(__name__)

class OllamaProvider(AIProvider):  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def __init__(self, host="http://localhost:11434", timeout=10):
        self.host = host
        self.timeout = timeout

    def generate_recommendation(self, telemetry):
        """Function docstring."""

        prompt = f"Analyze telemetry: {telemetry}"

        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"Timeout while contacting Ollama at {self.host}")  # pylint: disable=logging-fstring-interpolation
            return {"error": "Timeout", "recommendation": "None"}
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.host}. Is it running?")  # pylint: disable=logging-fstring-interpolation
            return {"error": "ConnectionError", "recommendation": "None"}
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(f"Unexpected error communicating with Ollama: {e}")  # pylint: disable=logging-fstring-interpolation
            return {"error": str(e), "recommendation": "None"}
