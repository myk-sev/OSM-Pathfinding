"""Django views for the pathfinding visualization app."""

from __future__ import annotations

from typing import Any

import folium
from django.shortcuts import render

from route_choices import ROUTES
from route_pipeline_service import run_route_pipeline

ALGORITHMS = (
    ("dijkstra", "Dijkstra"),
    ("astar", "A*"),
)


def _coords_from_compact_path(
    final_path: list[int],
    node_lookup: dict[int, dict[str, float]],
) -> list[tuple[float, float]]:
    """Convert compact node IDs from `final_path` into (lat, lon) coordinates."""
    coords: list[tuple[float, float]] = []
    for node_id in final_path:
        node = node_lookup.get(node_id)
        if node is None:
            continue
        coords.append((node["y"], node["x"]))
    return coords


def _build_folium_map(path_coords: list[tuple[float, float]]) -> str:
    """Create a Folium map HTML representation for the computed route."""
    if path_coords:
        center = path_coords[0]
    else:
        center = (41.5934, -87.3464)  # Fallback center (Northwest Indiana)

    route_map = folium.Map(location=center, zoom_start=14, control_scale=True)

    if path_coords:
        folium.Marker(path_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(route_map)
        folium.Marker(path_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(route_map)
        folium.PolyLine(path_coords, color="#1976d2", weight=6, opacity=0.9).add_to(route_map)

    return route_map._repr_html_()


def index(request):
    """Render form on GET and pathfinding results on POST."""
    context: dict[str, Any] = {
        "routes": ROUTES,
        "algorithms": ALGORITHMS,
        "selected_route": None,
        "selected_algorithm": "dijkstra",
    }

    if request.method != "POST":
        return render(request, "index.html", context)

    route_key = request.POST.get("route_key", "")
    algorithm = request.POST.get("algorithm", "dijkstra")

    context["selected_route"] = route_key
    context["selected_algorithm"] = algorithm

    try:
        graph, node_lookup, result = run_route_pipeline(route_key, algorithm)
        final_path = result.get("final_path", [])
        path_coords = _coords_from_compact_path(final_path, node_lookup)

        context.update(
            {
                "map_html": _build_folium_map(path_coords),
                "metrics": {
                    "algorithm": result.get("algorithm", algorithm),
                    "total_distance": result.get("total_distance", 0.0),
                    "nodes_visited": result.get("nodes_visited", 0),
                    "path_length": len(final_path),
                    "start": result.get("start"),
                    "end": result.get("end"),
                },
                "result": result,
                "graph": graph,
            }
        )
        return render(request, "results.html", context)
    except Exception as exc:  # Keep the form visible with a user-friendly error.
        context["error"] = str(exc)
        return render(request, "index.html", context)
