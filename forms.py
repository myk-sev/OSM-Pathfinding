"""Django form definitions for the pathfinding visualization app."""

from django import forms

from route_choices import DJANGO_ROUTE_CHOICES, ROUTE_BY_KEY

ALGORITHM_CHOICES = [
    ("dijkstra", "Dijkstra"),
    ("astar", "A*"),
    ("bellman_ford", "Bellman-Ford"),
]


class PathfindingForm(forms.Form):
    """Collects user-safe route and algorithm selections for pathfinding."""

    route = forms.ChoiceField(choices=DJANGO_ROUTE_CHOICES, required=True)
    algorithm = forms.ChoiceField(choices=ALGORITHM_CHOICES, required=True)

    def clean_route(self) -> str:
        """Only allow one of the predefined route keys."""
        route_key = self.cleaned_data["route"]
        if route_key not in ROUTE_BY_KEY:
            raise forms.ValidationError("Please choose one of the predefined routes.")
        return route_key

    def clean(self) -> dict[str, str]:
        """Reject payloads that try to inject raw coordinates."""
        cleaned_data = super().clean()

        blocked_coordinate_fields = {
            "start_lat",
            "start_lng",
            "end_lat",
            "end_lng",
            "start_coordinates",
            "end_coordinates",
        }
        provided_blocked_fields = blocked_coordinate_fields.intersection(self.data.keys())

        if provided_blocked_fields:
            raise forms.ValidationError(
                "Custom coordinates are not allowed. Please select a predefined route."
            )

        return cleaned_data
