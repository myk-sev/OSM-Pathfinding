"""Folium helpers for visualizing pathfinding output."""

from __future__ import annotations

from typing import Mapping, Sequence

import folium

from visualization.folium_map_builder import DEFAULT_TILES


def render_visited_order_map(
    visited_order: Sequence[int],
    node_lookup: Mapping[int, Mapping[str, float]],
    *,
    zoom_start: int = 15,
    marker_radius: float = 2.5,
) -> folium.Map:
    """Build a Folium map showing each visited node in traversal order.

    Args:
        visited_order: Compact node IDs in the order they were visited.
        node_lookup: Mapping from compact node ID to at least ``lat`` and ``lon``.
        zoom_start: Initial folium zoom value.
        marker_radius: Radius (px) used for circle markers.

    Returns:
        A ``folium.Map`` object with lightweight ``CircleMarker`` points added.

    Notes:
        This uses ``CircleMarker`` (canvas-backed in Leaflet) which is efficient enough
        for small class-project graphs while still showing progression.
    """
    if not visited_order:
        raise ValueError("visited_order must contain at least one node id")

    first_id = visited_order[0]
    if first_id not in node_lookup:
        raise KeyError(f"Node id {first_id} from visited_order is missing in node_lookup")

    start_meta = node_lookup[first_id]
    fmap = folium.Map(
        location=[start_meta["lat"], start_meta["lon"]],
        zoom_start=zoom_start,
        tiles=DEFAULT_TILES,
    )

    total = len(visited_order)
    for idx, node_id in enumerate(visited_order):
        if node_id not in node_lookup:
            continue

        node_meta = node_lookup[node_id]
        # Blue -> red gradient to show progression.
        frac = idx / max(total - 1, 1)
        red = int(255 * frac)
        blue = int(255 * (1.0 - frac))
        color = f"#{red:02x}00{blue:02x}"

        folium.CircleMarker(
            location=[node_meta["lat"], node_meta["lon"]],
            radius=marker_radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            weight=1,
            popup=f"step={idx}, node={node_id}",
        ).add_to(fmap)

    return fmap
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
        map_obj = folium.Map(location=coordinates[0], zoom_start=15, control_scale=True, tiles=DEFAULT_TILES)

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
