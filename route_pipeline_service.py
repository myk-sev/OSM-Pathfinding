"""Service utilities to run the OSM -> C++ pathfinding pipeline for predefined routes."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import osmnx as ox

from export_osmnx_graph import build_node_mappings, convert_edges, write_graph_input
from route_choices import ROUTE_BY_KEY

_GRAPH_CACHE: dict[str, Any] = {}


def _load_or_cache_graph(graphml_path: Path) -> Any:
    """Load an OSMnx graph from GraphML and cache it in-process by path."""
    cache_key = str(graphml_path.resolve())
    if cache_key not in _GRAPH_CACHE:
        _GRAPH_CACHE[cache_key] = ox.load_graphml(graphml_path)
    return _GRAPH_CACHE[cache_key]


def _compact_lookup(graph) -> tuple[dict[int, dict[str, float]], dict[int, int]]:
    compact_to_osm, lookup = build_node_mappings(graph)
    osm_to_compact = {osm_id: compact_id for compact_id, osm_id in compact_to_osm.items()}
    return lookup, osm_to_compact


def run_route_pipeline(route_key: str, algorithm: str) -> tuple[Any, dict[int, dict[str, float]], dict[str, Any]]:
    """Run full pipeline for one predefined route and return graph, node lookup, and result JSON.

    Steps:
    1) load/cached OSM graph,
    2) resolve nearest start/end OSM nodes from route coordinates,
    3) export graph_input.txt,
    4) call C++ pathfinder executable,
    5) parse JSON output,
    6) return (graph, node_lookup, result).
    """
    route = ROUTE_BY_KEY.get(route_key)
    if route is None:
        raise ValueError(f"Unknown route_key: {route_key}")

    repo_root = Path(__file__).resolve().parent
    graphml_path = repo_root / "ivy_tech_lake_county.graphml"
    graph_input_path = repo_root / "graph_input.txt"
    output_json_path = repo_root / "pathfinding_result.json"
    executable_path = repo_root / "pathfinder"

    if not graphml_path.exists():
        raise FileNotFoundError(
            f"Graph cache not found at {graphml_path}. Save OSM data to this GraphML path first."
        )

    graph = _load_or_cache_graph(graphml_path)

    start_osm = int(ox.distance.nearest_nodes(graph, X=route.start_lng, Y=route.start_lat))
    end_osm = int(ox.distance.nearest_nodes(graph, X=route.end_lng, Y=route.end_lat))

    node_lookup, osm_to_compact = _compact_lookup(graph)
    if start_osm not in osm_to_compact or end_osm not in osm_to_compact:
        raise ValueError("Nearest OSM nodes are not present in compact mapping")

    start_compact = osm_to_compact[start_osm]
    end_compact = osm_to_compact[end_osm]

    edges = convert_edges(graph, osm_to_compact)
    write_graph_input(graph_input_path, node_lookup, edges, start_compact, end_compact)

    if not executable_path.exists():
        raise FileNotFoundError(f"Missing pathfinder executable: {executable_path}")

    subprocess.run(
        [str(executable_path), str(graph_input_path), str(output_json_path), algorithm],
        check=True,
        cwd=repo_root,
    )

    result = json.loads(output_json_path.read_text(encoding="utf-8"))
    return graph, node_lookup, result
