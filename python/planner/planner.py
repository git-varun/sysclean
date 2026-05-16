"""Module docstring."""
class CleanupPlan:
    """Class docstring."""

    def __init__(self):
        self.operations = []
        self.estimated_reclaim_bytes = 0
        self.risk_score = 0

    def add_operation(self, operation):
        """Function docstring."""
        self.operations.append(operation)

    def summarize(self):
        """Function docstring."""
        return {
            "operations": len(self.operations),
            "estimated_reclaim_bytes": self.estimated_reclaim_bytes,
            "risk_score": self.risk_score,
        }
