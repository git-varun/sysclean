"""Module docstring."""  # pylint: disable=too-few-public-methods
class LocalAIRuntime:
    """Class docstring."""

    PROVIDERS = [
        "ollama",
        "llamacpp",
        "openai-compatible"
    ]

    def providers(self):
        """Function docstring."""

        return self.PROVIDERS
