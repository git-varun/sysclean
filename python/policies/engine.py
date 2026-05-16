"""Module docstring."""
import yaml


class PolicyEngine:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def __init__(self, policy_path):

        with open(policy_path, "r") as fh:  # pylint: disable=unspecified-encoding
            self.policy = yaml.safe_load(fh)

    def evaluate(self, telemetry):
        """Function docstring."""

        actions = []

        for rule in self.policy.get("rules", []):

            metric = rule["when"]["metric"]
            threshold = rule["when"]["greater_than"]

            if telemetry.get(metric, 0) > threshold:
                actions.append(rule["then"])

        return actions
