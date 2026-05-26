"""Provider factory for loading AI backends."""
import os
import logging
from ai.providers.ollama import OllamaProvider
from ai.providers.google_ai import GoogleAIProvider

logger = logging.getLogger(__name__)

class ProviderFactory:
    """Instantiates the correct AI Provider based on environment configuration."""

    @staticmethod
    def get_provider():
        """Returns an instance of an AIProvider."""
        env_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")
        env_path = os.path.abspath(env_path)
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if "=" in line:
                            k, v = line.split("=", 1)
                            os.environ.setdefault(k.strip(), v.strip())

        provider_name = os.environ.get("SYSCLEAN_AI_PROVIDER", "").lower()

        if not provider_name:
            if os.environ.get("GOOGLE_API_KEY"):
                provider_name = "google"
            else:
                provider_name = "ollama"

        if provider_name == "google":
            logger.info("Initializing Google AI Provider (gemini-2.5-flash).")
            return GoogleAIProvider()
        elif provider_name == "ollama":
            logger.info("Initializing local Ollama Provider.")
            return OllamaProvider(timeout=15)
        else:
            logger.warning(f"Unknown AI provider '{provider_name}'. Falling back to Ollama.")
            return OllamaProvider(timeout=15)
