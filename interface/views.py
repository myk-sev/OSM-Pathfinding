"""Django views for the pathfinding interface app."""

from __future__ import annotations

from typing import Any

import folium
from django.shortcuts import render

from services.route_pipeline_service import run_route_pipeline
from services.route_choices import ROUTE_CHOICES
from visualization.folium_map_builder import DEFAULT_TILES, build_result_map

from .forms import ALGORITHM_CHOICES, PathfindingForm



def _is_coordinate_pair(value: Any) -> bool:
    return (
        isinstance(value, (list, tuple))
        and len(value) == 2
        and all(isinstance(coord, (int, float)) for coord in value)
    )


def _coords_from_path_result(
    final_path: list[Any],
    node_lookup: dict[int, dict[str, float]],
) -> list[tuple[float, float]]:
    coords: list[tuple[float, float]] = []

    for path_item in final_path:
        if _is_coordinate_pair(path_item):
            lat, lon = path_item
            coords.append((float(lat), float(lon)))
            continue

        try:
            node_id = int(path_item)
        except (TypeError, ValueError):
            continue

        node = node_lookup.get(node_id)
        if node is None:
            continue
        coords.append((float(node["lat"]), float(node["lon"])))

    return coords



def _build_folium_map(path_coords: list[tuple[float, float]]) -> str:
    center = path_coords[0] if path_coords else (41.5934, -87.3464)
    route_map = folium.Map(location=center, zoom_start=14, control_scale=True, tiles=DEFAULT_TILES)

    if path_coords:
        folium.Marker(path_coords[0], tooltip="Start", icon=folium.Icon(color="green")).add_to(route_map)
        folium.Marker(path_coords[-1], tooltip="End", icon=folium.Icon(color="red")).add_to(route_map)
        folium.PolyLine(path_coords, color="#1976d2", weight=6, opacity=0.9).add_to(route_map)

    return route_map._repr_html_()


def _build_route_selection_map() -> str:
    route_map = folium.Map(
        location=(41.5859, -87.4737),
        zoom_start=10,
        control_scale=True,
        tiles=DEFAULT_TILES,
    )

    bounds: list[tuple[float, float]] = []
    colors = ["#2563eb", "#0f766e", "#c2410c", "#7c3aed"]

    for index, route in enumerate(ROUTE_CHOICES):
        start = (route.start_lat, route.start_lng)
        end = (route.end_lat, route.end_lng)
        color = colors[index % len(colors)]
        bounds.extend([start, end])

        folium.PolyLine(
            [start, end],
            color=color,
            weight=4,
            opacity=0.75,
            tooltip=route.display_name,
        ).add_to(route_map)
        folium.CircleMarker(
            location=start,
            radius=6,
            color="#15803d",
            fill=True,
            fill_color="#22c55e",
            fill_opacity=0.95,
            tooltip="Start: Ivy Tech Lake County",
        ).add_to(route_map)
        folium.CircleMarker(
            location=end,
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            tooltip=route.display_name,
        ).add_to(route_map)

    if bounds:
        route_map.fit_bounds(bounds, padding=(40, 40))

    return route_map._repr_html_()


def _build_result_map_html(
    graph: Any,
    node_lookup: dict[int, dict[str, float]],
    result: dict[str, Any],
    path_coords: list[tuple[float, float]],
) -> str:
    graph_edges = result.get("graph_edges")
    if graph_edges is not None:
        return build_result_map(graph_edges, node_lookup, result)
    return _build_folium_map(path_coords)



def index(request):
    form = PathfindingForm(request.POST or None)
    context: dict[str, Any] = {
        "form": form,
        "algorithm_choices": ALGORITHM_CHOICES,
        "map_html": _build_route_selection_map(),
    }

    if request.method == "POST" and form.is_valid():
        route_key = form.cleaned_data["route"]
        algorithm = form.cleaned_data["algorithm"]

        try:
            graph, node_lookup, result = run_route_pipeline(route_key, algorithm)
            final_path = result.get("final_path", [])
            path_coords = _coords_from_path_result(final_path, node_lookup)

            context.update(
                {
                    "map_html": _build_result_map_html(graph, node_lookup, result, path_coords),
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
