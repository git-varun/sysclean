"""Module docstring."""
from datetime import datetime


def generate_markdown(summary):
    """Function docstring."""

    report = f'''
# SysClean Report

Generated:
{datetime.utcnow().isoformat()}

## Summary

- Reclaimed MB:
  {summary["reclaimed_mb"]}

- Operations:
  {summary["operations"]}

- Failures:
  {summary["failures"]}
'''

    return report
