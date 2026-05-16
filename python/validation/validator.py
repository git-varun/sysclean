#!/usr/bin/env python3
"""Module docstring."""

import json
import pathlib
import sys

import yaml
from jsonschema import validate


def main() -> None:
    """Function docstring."""
    config_path = pathlib.Path(sys.argv[1])
    schema_path = pathlib.Path("config/schema.json")

    with config_path.open("r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    with schema_path.open("r", encoding="utf-8") as fh:
        schema = json.load(fh)

    validate(instance=config, schema=schema)

    print("Configuration validated")


if __name__ == "__main__":
    main()
