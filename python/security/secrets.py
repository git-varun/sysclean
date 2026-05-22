"""Module docstring."""
import re

SECRET_PATTERNS = [
    r"BEGIN RSA PRIVATE KEY",
    r"BEGIN OPENSSH PRIVATE KEY",
    r"mnemonic",
    r"api_key",
]


def contains_secret(content: str) -> bool:
    """Function docstring."""

    return any(
        re.search(pattern, content, re.IGNORECASE)
        for pattern in SECRET_PATTERNS
    )
