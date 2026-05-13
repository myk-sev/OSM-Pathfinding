from django.test import SimpleTestCase

from interface.forms import ALGORITHM_CHOICES
from interface.views import _coords_from_path_result
from services.graph_pathfinder import run_graph_pathfinder
from services.temp_folium_fixture import TEMP_FOLIUM_ROUTE_KEY, load_temp_folium_fixture
from visualization.folium_map_builder import build_result_map


class PathCoordinateTests(SimpleTestCase):
    def test_coordinate_pairs_are_used_directly(self) -> None:
        final_path = [
            [37.7749, -122.4194],
            [37.7783, -122.415],
        ]

        self.assertEqual(
            _coords_from_path_result(final_path, {}),
            [(37.7749, -122.4194), (37.7783, -122.415)],
        )

    def test_compact_ids_are_resolved_from_node_lookup(self) -> None:
        final_path = [10, "11"]
        node_lookup = {
            10: {"lat": 41.5859, "lon": -87.4737},
            11: {"lat": 41.6788, "lon": -87.4942},
        }

        self.assertEqual(
            _coords_from_path_result(final_path, node_lookup),
            [(41.5859, -87.4737), (41.6788, -87.4942)],
        )


class TemporaryFoliumFixtureTests(SimpleTestCase):
    def test_fixture_renders_full_folium_capacity_map(self) -> None:
        graph_edges, node_lookup, result = load_temp_folium_fixture()

        map_html = build_result_map(graph_edges, node_lookup, result)

        self.assertIn("Base Road Network", map_html)
        self.assertIn("Visited Traversal", map_html)
        self.assertIn("Final Path", map_html)
        self.assertIn("Route Metrics", map_html)
        self.assertIn("antPath", map_html)
        self.assertIn("Start node: 1", map_html)
        self.assertIn("End node: 5", map_html)

    def test_temporary_route_posts_through_django_view(self) -> None:
        response = self.client.post(
            "/",
            {"route": TEMP_FOLIUM_ROUTE_KEY, "algorithm": "dijkstra"},
        )

        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn("Pathfinding Results", content)
        self.assertIn("dijkstra (temporary Folium fixture)", content)
        self.assertIn("Base Road Network", content)
        self.assertIn("Visited Traversal", content)
        self.assertIn("Final Path", content)


class GraphPathfinderTests(SimpleTestCase):
    def test_form_offers_dijkstra_depth_first_and_breadth_first(self) -> None:
        self.assertEqual(
            ALGORITHM_CHOICES,
            [
                ("dijkstra", "Dijkstra"),
                ("dfs", "Depth First"),
                ("bfs", "Breadth-First"),
            ],
        )

    def test_pathfinder_uses_requested_start_and_end_nodes(self) -> None:
        node_lookup = {
            0: {"lat": 0.0, "lon": 0.0},
            1: {"lat": 0.0, "lon": 0.1},
            2: {"lat": 0.0, "lon": 0.2},
            3: {"lat": 1.0, "lon": 1.0},
        }
        edges = [
            (0, 1, 1.0),
            (1, 2, 1.0),
            (0, 3, 1.0),
        ]

        first = run_graph_pathfinder(node_lookup, edges, 0, 2, "dijkstra")
        second = run_graph_pathfinder(node_lookup, edges, 0, 3, "dijkstra")

        self.assertEqual(first["final_path"], [0, 1, 2])
        self.assertEqual(second["final_path"], [0, 3])

    def test_pathfinder_supports_weighted_and_unweighted_algorithms(self) -> None:
        node_lookup = {
            node_id: {"lat": 0.0, "lon": float(node_id)}
            for node_id in range(5)
        }
        edges = [
            (0, 1, 1.0),
            (0, 2, 5.0),
            (1, 3, 1.0),
            (3, 4, 1.0),
            (2, 4, 1.0),
        ]

        dijkstra = run_graph_pathfinder(node_lookup, edges, 0, 4, "dijkstra")
        depth_first = run_graph_pathfinder(node_lookup, edges, 0, 4, "dfs")
        breadth_first = run_graph_pathfinder(node_lookup, edges, 0, 4, "bfs")

        self.assertEqual(dijkstra["final_path"], [0, 1, 3, 4])
        self.assertEqual(dijkstra["total_distance"], 3.0)
        self.assertEqual(depth_first["final_path"], [0, 1, 3, 4])
        self.assertEqual(breadth_first["final_path"], [0, 2, 4])
        self.assertEqual(breadth_first["total_distance"], 6.0)

    def test_pathfinder_accepts_common_dijkstra_misspelling(self) -> None:
        result = run_graph_pathfinder(
            {0: {"lat": 0.0, "lon": 0.0}, 1: {"lat": 0.0, "lon": 1.0}},
            [(0, 1, 7.0)],
            0,
            1,
            "djikstras",
        )

        self.assertEqual(result["algorithm"], "dijkstra")
        self.assertEqual(result["final_path"], [0, 1])
