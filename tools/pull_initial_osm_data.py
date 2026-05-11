"""Pull and cache the initial OSMnx graph batch for all predefined route coordinates.

This tool builds one bounding area from every predefined start/end coordinate and
writes the GraphML file used by the pipeline at:
    services/ivy_tech_lake_county.graphml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from services.route_choices import ROUTE_CHOICES


def _compute_bounds(buffer_deg: float) -> tuple[float, float, float, float]:
    """Return (north, south, east, west) bounds covering all predefined routes."""
    lats: list[float] = []
    lngs: list[float] = []

    for route in ROUTE_CHOICES:
        lats.extend([route.start_lat, route.end_lat])
        lngs.extend([route.start_lng, route.end_lng])

    north = max(lats) + buffer_deg
    south = min(lats) - buffer_deg
    east = max(lngs) + buffer_deg
    west = min(lngs) - buffer_deg
    return north, south, east, west


def pull_initial_graph(output_path: Path, network_type: str, buffer_deg: float) -> Path:
    """Download and save graph data required by the route pipeline."""
    try:
        import osmnx as ox
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Missing dependency 'osmnx'. Install requirements first (for example: pip install -r requirements.txt)."
        ) from exc

    north, south, east, west = _compute_bounds(buffer_deg=buffer_deg)

    # OSMnx expects bbox ordering as (left, bottom, right, top) => (west, south, east, north).
    bbox = (west, south, east, north)
    graph = ox.graph_from_bbox(bbox=bbox, network_type=network_type, simplify=True)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    ox.save_graphml(graph, output_path)
    return output_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pull initial OSM data batch for the configured routes")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("services") / "ivy_tech_lake_county.graphml",
        help="GraphML output path (default: services/ivy_tech_lake_county.graphml)",
    )
    parser.add_argument(
        "--network-type",
        default="drive",
        choices=["all", "all_public", "bike", "drive", "drive_service", "walk"],
        help="OSMnx network_type to pull (default: drive)",
    )
    parser.add_argument(
        "--buffer-deg",
        type=float,
        default=0.02,
        help="Degree buffer added around route coordinate bounds (default: 0.02)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    north, south, east, west = _compute_bounds(buffer_deg=args.buffer_deg)
    print(f"Using bbox (west, south, east, north): {(west, south, east, north)}")

    out = pull_initial_graph(
        output_path=args.output,
        network_type=args.network_type,
        buffer_deg=args.buffer_deg,
    )
    print(f"Saved initial graph batch to: {out}")
