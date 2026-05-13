"""Django form definitions for the pathfinding interface app."""

from django import forms

from services.route_choices import DJANGO_ROUTE_CHOICES, ROUTE_BY_KEY

ALGORITHM_CHOICES = [
    ("dijkstra", "Dijkstra"),
    ("dfs", "Depth First"),
    ("bfs", "Breadth-First"),
]


class PathfindingForm(forms.Form):
    """Collect user route + algorithm selections for pathfinding."""

    route = forms.ChoiceField(choices=DJANGO_ROUTE_CHOICES, required=True)
    algorithm = forms.ChoiceField(choices=ALGORITHM_CHOICES, required=True)

    def clean_route(self) -> str:
        route_key = self.cleaned_data["route"]
        if route_key not in ROUTE_BY_KEY:
            raise forms.ValidationError("Please choose one of the predefined routes.")
        return route_key

    def clean(self) -> dict[str, str]:
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
