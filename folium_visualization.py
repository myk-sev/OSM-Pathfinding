"""Folium helpers for visualizing pathfinding output."""

from __future__ import annotations

from typing import Mapping, Sequence

import folium


def draw_final_path(
    final_path: Sequence[int],
    node_lookup: Mapping[int, Mapping[str, float]],
    map_obj: folium.Map | None = None,
) -> folium.Map:
    """Draw a final path as a clearly visible polyline plus start/end markers.

    Args:
        final_path: Ordered list of compact node IDs representing the solved route.
        node_lookup: Mapping of node ID -> {"lat": float, "lng": float}.
        map_obj: Optional existing Folium map to draw onto.

    Returns:
        Folium map containing the path line and endpoint markers.

    Raises:
        ValueError: If the path is empty or a node is missing/invalid.
    """
    if not final_path:
        raise ValueError("final_path cannot be empty")

    missing = [node_id for node_id in final_path if node_id not in node_lookup]
    if missing:
        raise ValueError(f"Missing node IDs in node_lookup: {missing[:5]}")

    coordinates: list[tuple[float, float]] = []
    for node_id in final_path:
        point = node_lookup[node_id]
        try:
            lat = float(point["lat"])
            lng = float(point["lng"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid coordinate data for node {node_id}: {point}") from exc
        coordinates.append((lat, lng))

    if map_obj is None:
        map_obj = folium.Map(location=coordinates[0], zoom_start=15, control_scale=True)

    folium.PolyLine(
        locations=coordinates,
        color="#0D47A1",
        weight=8,
        opacity=0.95,
        tooltip="Final Path",
    ).add_to(map_obj)

    folium.Marker(
        location=coordinates[0],
        popup=f"Start node: {final_path[0]}",
        tooltip="Start",
        icon=folium.Icon(color="green", icon="play"),
    ).add_to(map_obj)

    folium.Marker(
        location=coordinates[-1],
        popup=f"End node: {final_path[-1]}",
        tooltip="End",
        icon=folium.Icon(color="red", icon="stop"),
    ).add_to(map_obj)

    return map_obj
