"""Module docstring."""
import pathlib
import yaml


PLUGIN_DIRS = [
    pathlib.Path("modules"),
    pathlib.Path("plugins")
]


def discover_plugins():
    """Function docstring."""

    plugins = []

    for root in PLUGIN_DIRS:

        for manifest in root.rglob("manifest.yml"):

            data = yaml.safe_load(
                manifest.read_text()
            )

            plugins.append({
                "manifest": data,
                "path": manifest.parent
            })

    return plugins
