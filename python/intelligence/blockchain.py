"""Module docstring."""
from pathlib import Path


BLOCKCHAIN_DIRS = [
    ".foundry",
    ".ethereum",
    ".anvil",
    ".hardhat",
    ".solana"
]


class BlockchainAnalyzer:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    def locate_chain_data(self, home):
        """Function docstring."""

        findings = []

        for pattern in BLOCKCHAIN_DIRS:

            for path in Path(home).rglob(pattern):
                findings.append(str(path))

        return findings
