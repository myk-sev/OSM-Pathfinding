#!/usr/bin/env python3
"""Parser and validator for C++ pathfinding JSON output files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


REQUIRED_FIELDS = {
    "algorithm",
    "start",
    "end",
    "visited_order",
    "final_path",
    "total_distance",
    "nodes_visited",
}


def _validate_int_list(field_name: str, value: Any) -> None:
    if not isinstance(value, list):
        raise ValueError(f"'{field_name}' must be a list")
    if not all(isinstance(item, int) for item in value):
        raise ValueError(f"'{field_name}' must contain only integers")


def parse_pathfinding_json(path: str | Path) -> Dict[str, Any]:
    """Load and validate a pathfinding JSON output file.

    Args:
        path: Path to the JSON file.

    Returns:
        The parsed JSON object as a dictionary.

    Raises:
        ValueError: If required fields are missing or field types are invalid.
        json.JSONDecodeError: If the file content is not valid JSON.
        OSError: If the file cannot be read.
    """
    file_path = Path(path)

    with file_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        raise ValueError("JSON root must be an object")

    missing = REQUIRED_FIELDS - data.keys()
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise ValueError(f"Missing required field(s): {missing_fields}")

    _validate_int_list("final_path", data["final_path"])
    _validate_int_list("visited_order", data["visited_order"])

    return data


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Parse and validate pathfinding JSON output")
    parser.add_argument("json_file", help="Path to JSON file")
    args = parser.parse_args()

    parsed = parse_pathfinding_json(args.json_file)
    print("Valid pathfinding output JSON.")
    print(json.dumps(parsed, indent=2))
