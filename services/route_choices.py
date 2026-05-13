"""Predefined route choices for Ivy Tech – Lake County nearby trips.

This module is designed for Django forms so users can only pick from
approved routes instead of submitting arbitrary coordinates.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteChoice:
    """One allowed start/end route pair."""

    key: str
    display_name: str
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float


ROUTE_CHOICES = [
    RouteChoice(
        key="to_hammond_station",
        display_name="Ivy Tech Lake County → Hammond-Whiting Amtrak Station",
        start_lat=41.5859,
        start_lng=-87.4737,
        end_lat=41.6788,
        end_lng=-87.4942,
    ),
    RouteChoice(
        key="to_indiana_dunes",
        display_name="Ivy Tech Lake County → Indiana Dunes Visitor Center",
        start_lat=41.5859,
        start_lng=-87.4737,
        end_lat=41.6600,
        end_lng=-87.0414,
    ),
    RouteChoice(
        key="to_crown_point_square",
        display_name="Ivy Tech Lake County → Crown Point Courthouse Square",
        start_lat=41.5859,
        start_lng=-87.4737,
        end_lat=41.4170,
        end_lng=-87.3653,
    ),
]

# Useful for Django forms. Example:
# route = forms.ChoiceField(choices=DJANGO_ROUTE_CHOICES)
DJANGO_ROUTE_CHOICES = [(route.key, route.display_name) for route in ROUTE_CHOICES]

# Useful lookup after form validation.
ROUTE_BY_KEY = {route.key: route for route in ROUTE_CHOICES}
