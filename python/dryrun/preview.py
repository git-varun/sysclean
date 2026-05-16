"""Module docstring."""
def render_preview(plan):
    """Function docstring."""

    print()
    print("========== DRY RUN ==========")

    print(
        f"Operations: {len(plan.operations)}"
    )

    print(
        f"Estimated reclaim: "
        f"{plan.estimated_reclaim_bytes / 1024 / 1024:.2f} MB"
    )

    print(
        f"Risk score: {plan.risk_score}"
    )

    print()
