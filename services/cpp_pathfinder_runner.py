"""Helpers to run the compiled C++ pathfinding executable."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


class CppPathfinderError(RuntimeError):
    """Raised when the C++ pathfinder executable fails."""


def _resolve_executable() -> str:
    """Resolve the pathfinding executable path with cross-platform defaults."""
    explicit = os.environ.get("CPP_PATHFINDER_EXECUTABLE")
    if explicit:
        return explicit

    candidates = ["pathfinder", "pathfinding_json_output"]
    if sys.platform.startswith("win"):
        candidates = [f"{name}.exe" for name in candidates] + candidates

    search_roots = [Path.cwd(), Path(__file__).resolve().parent.parent]
    for root in search_roots:
        for candidate in candidates:
            resolved = root / candidate
            if resolved.exists():
                return str(resolved)

    return candidates[0]

def run_cpp_pathfinder(input_path: str | os.PathLike[str], output_path: str | os.PathLike[str], algorithm: str) -> dict[str, Any]:
    """Run the compiled C++ pathfinder and return its JSON output.

    The executable path can be overridden with ``CPP_PATHFINDER_EXECUTABLE``;
    by default it uses ``./pathfinding_json_output``.
    """

    executable = _resolve_executable()
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
        hint = ""
        if "WinError 193" in str(exc):
            hint = (
                "\nThis often means the selected executable is built for a different OS/architecture. "
                "On Windows, ensure CPP_PATHFINDER_EXECUTABLE points to a valid .exe built for Windows."
            )
        raise CppPathfinderError(
            f"Failed to start pathfinder executable '{executable}': {exc}{hint}"
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
