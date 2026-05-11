"""Map predefined lat/lon pairs to compact graph node IDs.

This script:
1) loads an OSMnx graph,
2) finds nearest OSM node IDs for predefined coordinates, and
3) converts those OSM node IDs into compact integer IDs used by a C++ graph file.

Expected mapping file format
---------------------------
A CSV (or TSV) with at least these columns:
- compact_id: integer ID used by your C++ graph input
- osm_node_id: corresponding OSM node ID

Column names can be customized with CLI flags.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Iterable, Sequence

import osmnx as ox

# Replace these with your real coordinate pairs.
# (start_lat, start_lon, end_lat, end_lon)
ROUTE_COORD_PAIRS: list[tuple[float, float, float, float]] = [
    (37.7749, -122.4194, 37.7849, -122.4094),
    (40.7128, -74.0060, 40.7306, -73.9352),
]


def load_osm_to_compact_mapping(
    mapping_path: Path,
    compact_col: str,
    osm_col: str,
    delimiter: str,
) -> dict[int, int]:
    """Return dict: OSM node ID -> compact integer ID."""
    osm_to_compact: dict[int, int] = {}

    with mapping_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=delimiter)
        required = {compact_col, osm_col}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(
                f"Missing required columns {sorted(missing)} in {mapping_path}. "
                f"Found: {reader.fieldnames}"
            )

        for row in reader:
            compact_id = int(row[compact_col])
            osm_node_id = int(row[osm_col])
            osm_to_compact[osm_node_id] = compact_id

    return osm_to_compact


def nearest_osm_nodes_for_pairs(
    graph,
    coord_pairs: Sequence[tuple[float, float, float, float]],
) -> list[tuple[int, int]]:
    """Return (start_osm_node, end_osm_node) for each start/end coordinate pair."""
    nearest_nodes: list[tuple[int, int]] = []
    for start_lat, start_lon, end_lat, end_lon in coord_pairs:
        start_node = int(ox.distance.nearest_nodes(graph, X=start_lon, Y=start_lat))
        end_node = int(ox.distance.nearest_nodes(graph, X=end_lon, Y=end_lat))
        nearest_nodes.append((start_node, end_node))
    return nearest_nodes


def convert_osm_to_compact(
    osm_node_pairs: Iterable[tuple[int, int]],
    osm_to_compact: dict[int, int],
) -> list[tuple[int, int]]:
    """Convert each (start_osm, end_osm) pair into (start_compact, end_compact)."""
    compact_pairs: list[tuple[int, int]] = []

    for start_osm, end_osm in osm_node_pairs:
        if start_osm not in osm_to_compact:
            raise KeyError(f"Start OSM node {start_osm} not found in mapping file")
        if end_osm not in osm_to_compact:
            raise KeyError(f"End OSM node {end_osm} not found in mapping file")

        compact_pairs.append((osm_to_compact[start_osm], osm_to_compact[end_osm]))

    return compact_pairs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--graphml",
        type=Path,
        required=True,
        help="Path to OSMnx GraphML file (e.g. saved via ox.save_graphml).",
    )
    parser.add_argument(
        "--mapping-file",
        type=Path,
        required=True,
        help="CSV/TSV mapping file containing compact and OSM node ID columns.",
    )
    parser.add_argument(
        "--compact-col",
        default="compact_id",
        help="Column name for compact integer IDs.",
    )
    parser.add_argument(
        "--osm-col",
        default="osm_node_id",
        help="Column name for OSM node IDs.",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="Delimiter for mapping file (default: ','). Use '\\t' for TSV.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    graph = ox.load_graphml(args.graphml)

    osm_to_compact = load_osm_to_compact_mapping(
        mapping_path=args.mapping_file,
        compact_col=args.compact_col,
        osm_col=args.osm_col,
        delimiter=args.delimiter.encode("utf-8").decode("unicode_escape"),
    )

    osm_pairs = nearest_osm_nodes_for_pairs(graph, ROUTE_COORD_PAIRS)
    compact_pairs = convert_osm_to_compact(osm_pairs, osm_to_compact)

    print("Resolved routes:")
    for i, ((start_osm, end_osm), (start_compact, end_compact)) in enumerate(
        zip(osm_pairs, compact_pairs), start=1
    ):
        print(
            f"{i}. OSM nodes: {start_osm} -> {end_osm} | "
            f"Compact IDs: {start_compact} -> {end_compact}"
        )


if __name__ == "__main__":
    main()
