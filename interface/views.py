"""Django views for the pathfinding interface app."""

from __future__ import annotations

from typing import Any

import folium
from django.shortcuts import render

from services.route_pipeline_service import run_route_pipeline

from .forms import ALGORITHM_CHOICES, PathfindingForm



def _coords_from_compact_path(
    final_path: list[int],
    node_lookup: dict[int, dict[str, float]],
) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []
    for node_id in final_path:
        node = node_lookup.get(node_id)
        if node is None:
            continue
        coords.append((node["y"], node["x"]))
    return coords



def _build_folium_map(path_coords: list[tuple[float, float]]) -> str:
    center = path_coords[0] if path_coords else (41.5934, -87.3464)
    route_map = folium.Map(location=center, zoom_start=14, control_scale=True)

    if path_coords:
        folium.Marker(path_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(route_map)
        folium.Marker(path_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(route_map)
        folium.PolyLine(path_coords, color="#1976d2", weight=6, opacity=0.9).add_to(route_map)

    return route_map._repr_html_()



def index(request):
    form = PathfindingForm(request.POST or None)
    context: dict[str, Any] = {
        "form": form,
        "algorithm_choices": ALGORITHM_CHOICES,
    }

    if request.method == "POST" and form.is_valid():
        route_key = form.cleaned_data["route"]
        algorithm = form.cleaned_data["algorithm"]

        try:
            _graph, node_lookup, result = run_route_pipeline(route_key, algorithm)
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
                    "selected_route": route_key,
                }
            )
            return render(request, "interface/results.html", context)
        except Exception as exc:
            context["error"] = str(exc)

    return render(request, "interface/index.html", context)
