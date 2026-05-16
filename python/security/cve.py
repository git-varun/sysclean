"""Module docstring."""
import requests


class CVEEngine:  # pylint: disable=too-few-public-methods
    """Class docstring."""

    OSV_API = (
        "https://api.osv.dev/v1/query"
    )

    def query_package(self, package):
        """Function docstring."""

        payload = {
            "package": {
                "name": package
            }
        }

        response = requests.post(
            self.OSV_API,
            json=payload,
            timeout=10
        )

        return response.json()
