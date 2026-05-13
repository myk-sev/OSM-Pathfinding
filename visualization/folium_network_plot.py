"""Folium helpers for visualizing simplified road graphs."""

from __future__ import annotations

from typing import Mapping, Sequence

import folium

from visualization.folium_map_builder import DEFAULT_TILES


def draw_road_network(
    road_graph: Mapping[int, Sequence[int]],
    node_lookup: Mapping[int, Mapping[str, float]],
    *,
    zoom_start: int = 13,
    line_color: str = "#b9c2cf",
    line_weight: float = 1.5,
    line_opacity: float = 0.7,
) -> folium.Map:
    """Render a simplified road network as light polylines on a Folium map.

    Args:
        road_graph: Adjacency mapping of node_id -> iterable of neighboring node IDs.
        node_lookup: Mapping of node_id -> coordinate dictionary containing
            either ``{"lat", "lon"}`` or ``{"y", "x"}`` keys.
        zoom_start: Initial map zoom.
        line_color: Polyline color for roads.
        line_weight: Polyline width in pixels.
        line_opacity: Polyline opacity from 0 to 1.

    Returns:
        A ``folium.Map`` instance with all valid road segments drawn.
    """
    if not node_lookup:
        raise ValueError("node_lookup cannot be empty")

    def coords_for(node_id: int) -> tuple[float, float]:
        node = node_lookup[node_id]
        if "lat" in node and "lon" in node:
            return float(node["lat"]), float(node["lon"])
        if "y" in node and "x" in node:
            return float(node["y"]), float(node["x"])
        raise KeyError(f"Node {node_id} must include (lat, lon) or (y, x)")

    first_node_id = next(iter(node_lookup))
    center_lat, center_lon = coords_for(first_node_id)
    fmap = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_start, tiles=DEFAULT_TILES)

    drawn_segments: set[tuple[int, int]] = set()
    for source, neighbors in road_graph.items():
        if source not in node_lookup:
            continue
        for target in neighbors:
            if target not in node_lookup:
                continue

            segment = tuple(sorted((int(source), int(target))))
            if segment in drawn_segments:
                continue

            src_lat, src_lon = coords_for(int(source))
            dst_lat, dst_lon = coords_for(int(target))
            folium.PolyLine(
                locations=[(src_lat, src_lon), (dst_lat, dst_lon)],
                color=line_color,
                weight=line_weight,
                opacity=line_opacity,
            ).add_to(fmap)
            drawn_segments.add(segment)

    return fmap
