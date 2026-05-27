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
        # Search for .env in candidate paths (most specific to least specific)
        home = os.path.expanduser("~")
        candidate_paths = [
            os.path.join(home, ".config", "sysclean", ".env"),
            os.path.join(home, ".local", "share", "sysclean", ".env"),
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env")),
            os.path.join(os.getcwd(), ".env"),
        ]

        for env_path in candidate_paths:
            if os.path.exists(env_path):
                logger.info(f"Loading env from {env_path}")
                try:
                    with open(env_path, "r", encoding="utf-8") as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith("#"):
                                if "=" in line:
                                    k, v = line.split("=", 1)
                                    os.environ.setdefault(k.strip(), v.strip())
                except Exception as e:
                    logger.warning(f"Failed to read env file at {env_path}: {e}")

        provider_name = os.environ.get("SYSCLEAN_AI_PROVIDER", "").lower()

        if not provider_name:
            if os.environ.get("GOOGLE_API_KEY"):
                provider_name = "google"
            else:
                provider_name = "ollama"

        if provider_name == "google":
            logger.info("Initializing Google AI Provider (gemini-2.5-flash).")
            primary = GoogleAIProvider()
        elif provider_name == "ollama":
            logger.info("Initializing local Ollama Provider.")
            primary = OllamaProvider(timeout=15)
        else:
            logger.warning(f"Unknown AI provider '{provider_name}'. Falling back to Ollama.")
            primary = OllamaProvider(timeout=15)

        return SafeFallbackWrapperProvider(primary)


class SafeFallbackWrapperProvider:
    """Delegates to primary AI Provider and falls back to Heuristics if it fails or is offline."""

    def __init__(self, primary_provider):
        self.primary = primary_provider

    def generate_recommendation(self, telemetry):
        try:
            res = self.primary.generate_recommendation(telemetry)
            if isinstance(res, dict) and "error" in res:
                logger.warning(f"Primary AI Provider returned error: {res['error']}. Falling back to heuristics.")
                from ai.providers.fallback_ai import FallbackAIProvider
                return FallbackAIProvider().generate_recommendation(telemetry)
            return res
        except Exception as e:
            logger.warning(f"Primary AI Provider failed with exception: {e}. Falling back to heuristics.")
            from ai.providers.fallback_ai import FallbackAIProvider
            return FallbackAIProvider().generate_recommendation(telemetry)

