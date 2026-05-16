"""Module docstring."""  # pylint: disable=too-few-public-methods
class PolicyCompiler:
    """Class docstring."""

    def compile(
        self,
        policy
    ):
        """Function docstring."""

        compiled = []

        for rule in policy["rules"]:

            compiled.append({
                "condition": rule["when"],
                "action": rule["then"]
            })

        return compiled
