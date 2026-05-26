"""Google Generative AI Provider."""
import os
import logging
from google import genai
from google.genai.errors import APIError

from ai.providers.base import AIProvider

logger = logging.getLogger(__name__)

class GoogleAIProvider(AIProvider):
    """Google Generative AI backend for SysClean."""

    def __init__(self, model_name="gemini-2.5-flash"):
        self.model_name = model_name
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        if self.api_key:
            self.client = genai.Client(api_key=self.api_key)
        else:
            self.client = None

    def generate_recommendation(self, telemetry):
        """Generates a recommendation based on telemetry using Gemini."""
        if not self.client:
            logger.error("GOOGLE_API_KEY is not set. Cannot use GoogleAIProvider.")
            return {"error": "Missing GOOGLE_API_KEY environment variable", "recommendation": "None"}

        prompt = (
            "You are an AI assistant for SysClean, an automated workstation cleanup platform. "
            "Please analyze the following system telemetry and provide a brief, actionable recommendation "
            "on what can be safely cleaned up or optimized. Do not execute any commands.\n\n"
            f"Telemetry data:\n{telemetry}"
        )

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return {"response": response.text}
        except APIError as e:
            logger.error(f"Google API Error: {e}")
            return {"error": f"Google API Error: {str(e)}", "recommendation": "None"}
        except Exception as e:
            logger.error(f"Unexpected error communicating with Google AI: {e}")
            return {"error": str(e), "recommendation": "None"}
