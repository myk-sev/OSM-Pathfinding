"""Folium helpers for visualizing pathfinding traversal progress."""

from __future__ import annotations

from typing import Mapping, Sequence

import folium


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
    fmap = folium.Map(location=[start_meta["lat"], start_meta["lon"]], zoom_start=zoom_start)

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
