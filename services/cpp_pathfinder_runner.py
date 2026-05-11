"""Helpers to run the compiled C++ pathfinding executable."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


class CppPathfinderError(RuntimeError):
    """Raised when the C++ pathfinder executable fails."""


def run_cpp_pathfinder(input_path: str | os.PathLike[str], output_path: str | os.PathLike[str], algorithm: str) -> dict[str, Any]:
    """Run the compiled C++ pathfinder and return its JSON output.

    The executable path can be overridden with ``CPP_PATHFINDER_EXECUTABLE``;
    by default it uses ``./pathfinding_json_output``.
    """

    executable = os.environ.get("CPP_PATHFINDER_EXECUTABLE", "./pathfinding_json_output")
    input_file = Path(input_path)
    output_file = Path(output_path)

    cmd = [executable, str(input_file), str(output_file), algorithm]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise CppPathfinderError(
            f"Failed to start pathfinder executable '{executable}': {exc}"
        ) from exc

    if result.returncode != 0:
        raise CppPathfinderError(
            "C++ pathfinder failed "
            f"(exit code {result.returncode}).\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout:\n{result.stdout.strip() or '<empty>'}\n"
            f"stderr:\n{result.stderr.strip() or '<empty>'}"
        )

    if not output_file.exists():
        raise CppPathfinderError(
            f"C++ pathfinder reported success but did not create output file: {output_file}"
        )

    try:
        return json.loads(output_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CppPathfinderError(
            "C++ pathfinder returned invalid JSON in output file "
            f"'{output_file}': {exc}"
        ) from exc
