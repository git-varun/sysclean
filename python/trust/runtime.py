"""Module docstring."""  # pylint: disable=too-few-public-methods
class ZeroTrustRuntime:
    """Class docstring."""

    TRUSTED_CAPABILITIES = [
        "filesystem_read",
        "telemetry_read",
        "cleanup_safe"
    ]

    def validate(
        self,
        plugin
    ):
        """Function docstring."""

        requested = plugin.get(
            "capabilities",
            []
        )

        violations = [
            cap
            for cap in requested
            if cap not in self.TRUSTED_CAPABILITIES
        ]

        return {
            "trusted": len(violations) == 0,
            "violations": violations
        }
