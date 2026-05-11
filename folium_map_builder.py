"""Folium map rendering helpers for pathfinding results."""

from __future__ import annotations

from typing import Any

import folium
from folium.plugins import AntPath


def _node_latlon(node_lookup: dict[int, dict[str, float]], node_id: int) -> tuple[float, float]:
    node = node_lookup[int(node_id)]
    return float(node["lat"]), float(node["lon"])


def _to_int_lookup(node_lookup: dict[Any, dict[str, float]]) -> dict[int, dict[str, float]]:
    return {int(k): v for k, v in node_lookup.items()}


def build_result_map(
    graph_edges: list[tuple[int, int, float]],
    node_lookup: dict[Any, dict[str, float]],
    result: dict[str, Any],
) -> str:
    """Build a complete Folium HTML map for a pathfinding run.

    Args:
        graph_edges: Edge list as (u, v, length_m) using compact node IDs.
        node_lookup: Mapping of compact node ID -> {lat, lon, osm_id}.
        result: Pathfinding output with at least start, end, visited_order, final_path,
            total_distance, and nodes_visited.

    Returns:
        Rendered map HTML string suitable for embedding in a Django template.
    """
    lookup = _to_int_lookup(node_lookup)

    start_id = int(result["start"])
    end_id = int(result["end"])
    visited_order = [int(n) for n in result.get("visited_order", [])]
    final_path = [int(n) for n in result.get("final_path", [])]

    center = _node_latlon(lookup, start_id)
    fmap = folium.Map(location=center, zoom_start=15, control_scale=True, tiles="CartoDB positron")

    # 1) Base road network
    base_layer = folium.FeatureGroup(name="Base Road Network", show=True)
    for u, v, _ in graph_edges:
        if u not in lookup or v not in lookup:
            continue
        folium.PolyLine(
            locations=[_node_latlon(lookup, u), _node_latlon(lookup, v)],
            color="#8a8a8a",
            weight=1.2,
            opacity=0.35,
        ).add_to(base_layer)
    base_layer.add_to(fmap)

    # 2) Visited traversal order
    visited_layer = folium.FeatureGroup(name="Visited Traversal", show=True)
    visited_points = [_node_latlon(lookup, node_id) for node_id in visited_order if node_id in lookup]
    if len(visited_points) >= 2:
        AntPath(
            locations=visited_points,
            color="#2c7fb8",
            weight=3,
            opacity=0.8,
            delay=700,
            dash_array=[10, 18],
            pulse_color="#7fcdbb",
        ).add_to(visited_layer)
    for i, node_id in enumerate(visited_order, start=1):
        if node_id not in lookup:
            continue
        folium.CircleMarker(
            location=_node_latlon(lookup, node_id),
            radius=2,
            color="#2c7fb8",
            fill=True,
            fill_opacity=0.6,
            popup=f"Visited #{i}: node {node_id}",
        ).add_to(visited_layer)
    visited_layer.add_to(fmap)

    # 3) Final path
    path_layer = folium.FeatureGroup(name="Final Path", show=True)
    path_points = [_node_latlon(lookup, node_id) for node_id in final_path if node_id in lookup]
    if len(path_points) >= 2:
        folium.PolyLine(path_points, color="#d7191c", weight=6, opacity=0.95).add_to(path_layer)
    path_layer.add_to(fmap)

    # 4/5) Start and end markers
    folium.Marker(
        location=_node_latlon(lookup, start_id),
        popup=f"Start node: {start_id}",
        tooltip="Start",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(fmap)
    folium.Marker(
        location=_node_latlon(lookup, end_id),
        popup=f"End node: {end_id}",
        tooltip="End",
        icon=folium.Icon(color="red", icon="stop"),
    ).add_to(fmap)

    # 6) Metrics popup/legend
    algorithm = result.get("algorithm", "unknown")
    total_distance = result.get("total_distance", "n/a")
    nodes_visited = result.get("nodes_visited", len(visited_order))
    metrics_html = f"""
    <div style=\"position: fixed; bottom: 20px; left: 20px; z-index: 9999;
                background: white; border: 1px solid #bbb; border-radius: 8px;
                padding: 10px 12px; font-size: 13px; min-width: 200px;\">
      <div style=\"font-weight: 700; margin-bottom: 6px;\">Route Metrics</div>
      <div><b>Algorithm:</b> {algorithm}</div>
      <div><b>Total distance:</b> {total_distance} m</div>
      <div><b>Visited nodes:</b> {nodes_visited}</div>
      <div><b>Path nodes:</b> {len(final_path)}</div>
    </div>
    """
    fmap.get_root().html.add_child(folium.Element(metrics_html))

    folium.LayerControl(collapsed=False).add_to(fmap)
    return fmap.get_root().render()
