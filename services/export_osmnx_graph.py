"""Export an OSMnx/NetworkX road graph into compact integer-node text inputs.

Outputs:
1) node_lookup.json
2) graph_input.txt
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import networkx as nx
import osmnx as ox


def build_node_mappings(graph: nx.MultiDiGraph) -> tuple[dict[int, int], dict[int, dict[str, float]]]:
    """Create compact node IDs [0..N-1] and lookup metadata."""
    osm_nodes = list(graph.nodes())
    compact_to_osm = {i: osm_id for i, osm_id in enumerate(osm_nodes)}

    lookup: dict[int, dict[str, float]] = {}
    for compact_id, osm_id in compact_to_osm.items():
        node_data: dict[str, Any] = graph.nodes[osm_id]
        lookup[compact_id] = {
            "osm_id": int(osm_id),
            "lat": float(node_data["y"]),
            "lon": float(node_data["x"]),
        }

    return compact_to_osm, lookup


def convert_edges(
    graph: nx.MultiDiGraph, osm_to_compact: dict[int, int]
) -> list[tuple[int, int, float]]:
    """Convert graph edges into compact-ID tuples: (u, v, length_m)."""
    converted: list[tuple[int, int, float]] = []
    for u, v, data in graph.edges(data=True):
        cu = osm_to_compact[int(u)]
        cv = osm_to_compact[int(v)]
        length = float(data.get("length", 1.0))
        converted.append((cu, cv, length))
    return converted


def write_node_lookup(path: Path, lookup: dict[int, dict[str, float]]) -> None:
    """Write JSON mapping compact IDs to original OSM IDs and coordinates."""
    # JSON object keys are strings; this keeps IDs readable for C++ lookup.
    serializable = {str(k): v for k, v in lookup.items()}
    path.write_text(json.dumps(serializable, indent=2), encoding="utf-8")


def write_graph_input(
    path: Path,
    lookup: dict[int, dict[str, float]],
    edges: list[tuple[int, int, float]],
    start_compact: int,
    end_compact: int,
) -> None:
    """Write simple line-oriented text for direct C++ file input."""
    n = len(lookup)
    m = len(edges)

    lines: list[str] = []
    lines.append(f"{n} {m}")
    lines.append("# NODES: compact_id lat lon")
    for cid in range(n):
        row = lookup[cid]
        lines.append(f"{cid} {row['lat']:.8f} {row['lon']:.8f}")

    lines.append("# EDGES: from_compact_id to_compact_id length_m")
    for u, v, w in edges:
        lines.append(f"{u} {v} {w:.3f}")

    lines.append("START_END")
    lines.append(f"{start_compact} {end_compact}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_graph(
    graphml_path: Path,
    out_dir: Path,
    start_osm_id: int,
    end_osm_id: int,
) -> None:
    graph = ox.load_graphml(graphml_path)
    compact_to_osm, lookup = build_node_mappings(graph)
    osm_to_compact = {osm: cid for cid, osm in compact_to_osm.items()}

    if start_osm_id not in osm_to_compact:
        raise ValueError(f"start_osm_id {start_osm_id} not found in graph")
    if end_osm_id not in osm_to_compact:
        raise ValueError(f"end_osm_id {end_osm_id} not found in graph")

    edges = convert_edges(graph, osm_to_compact)
    start_compact = osm_to_compact[start_osm_id]
    end_compact = osm_to_compact[end_osm_id]

    out_dir.mkdir(parents=True, exist_ok=True)
    write_node_lookup(out_dir / "node_lookup.json", lookup)
    write_graph_input(out_dir / "graph_input.txt", lookup, edges, start_compact, end_compact)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export OSMnx graph to compact C++-friendly text")
    parser.add_argument("--graphml", required=True, type=Path, help="Input GraphML file from OSMnx")
    parser.add_argument("--out-dir", required=True, type=Path, help="Output directory")
    parser.add_argument("--start-osm-id", required=True, type=int, help="OSM node ID for start")
    parser.add_argument("--end-osm-id", required=True, type=int, help="OSM node ID for end")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    export_graph(args.graphml, args.out_dir, args.start_osm_id, args.end_osm_id)
