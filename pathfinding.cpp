#include <algorithm>
#include <cmath>
#include <fstream>
#include <functional>
#include <limits>
#include <queue>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

struct Edge {
    int to;
    double weight;
};

using Graph = std::unordered_map<int, std::vector<Edge>>;

struct PathfindingResult {
    std::vector<int> path;
    std::vector<int> permanently_visited_order;
    double distance = std::numeric_limits<double>::infinity();
};

PathfindingResult dijkstra_with_visit_order(const Graph& graph, int source, int target) {
    PathfindingResult result;

    std::unordered_map<int, double> distance;
    std::unordered_map<int, int> previous;
    std::unordered_set<int> settled;

    using QueueState = std::pair<double, int>; // (distance, node)
    std::priority_queue<QueueState, std::vector<QueueState>, std::greater<QueueState>> frontier;

    distance[source] = 0.0;
    frontier.push({0.0, source});

    while (!frontier.empty()) {
        auto [dist_u, u] = frontier.top();
        frontier.pop();

        if (settled.count(u) > 0) {
            continue;
        }

        // This is the moment node u becomes permanently visited.
        settled.insert(u);
        result.permanently_visited_order.push_back(u);

        if (u == target) {
            break;
        }

        auto it = graph.find(u);
        if (it == graph.end()) {
            continue;
        }

        for (const Edge& edge : it->second) {
            if (settled.count(edge.to) > 0) {
                continue;
            }

            const double alt = dist_u + edge.weight;
            if (!distance.count(edge.to) || alt < distance[edge.to]) {
                distance[edge.to] = alt;
                previous[edge.to] = u;
                frontier.push({alt, edge.to});
            }
        }
    }

    if (!distance.count(target)) {
        return result;
    }

    result.distance = distance[target];

    for (int at = target;; at = previous[at]) {
        result.path.push_back(at);
        if (at == source) {
            break;
        }
    }
    std::reverse(result.path.begin(), result.path.end());

    return result;
}

void write_result_json(const PathfindingResult& result, const std::string& output_file) {
    std::ofstream out(output_file);

    out << "{\n";

    out << "  \"path\": [";
    for (size_t i = 0; i < result.path.size(); ++i) {
        out << result.path[i];
        if (i + 1 != result.path.size()) {
            out << ", ";
        }
    }
    out << "],\n";

    out << "  \"permanently_visited_order\": [";
    for (size_t i = 0; i < result.permanently_visited_order.size(); ++i) {
        out << result.permanently_visited_order[i];
        if (i + 1 != result.permanently_visited_order.size()) {
            out << ", ";
        }
    }
    out << "],\n";

    if (std::isfinite(result.distance)) {
        out << "  \"distance\": " << result.distance << "\n";
    } else {
        out << "  \"distance\": null\n";
    }

    out << "}\n";
}
