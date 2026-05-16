"""Module docstring."""
ALLOWED_CAPABILITIES = {
    "filesystem",
    "apt",
    "docker",
    "snap",
    "telemetry"
}


def validate_capabilities(plugin):
    """Function docstring."""

    requested = set(
        plugin["manifest"].get(
            "capabilities",
            []
        )
    )

    forbidden = (
        requested - ALLOWED_CAPABILITIES
    )

    if forbidden:
        raise RuntimeError(
            f"Forbidden capabilities: {forbidden}"
        )
