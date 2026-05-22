"""Module docstring."""
PROTECTED_PATTERNS = [
    ".env",
    "wallet",
    "keystore",
    "mnemonic",
    ".pem",
    ".ssh",
    ".gnupg",
    "validator"
]


def is_protected(path: str) -> bool:
    """Function docstring."""

    lowered = path.lower()

    return any(
        pattern in lowered
        for pattern in PROTECTED_PATTERNS
    )
