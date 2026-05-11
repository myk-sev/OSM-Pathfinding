#include <algorithm>
#include <iostream>
#include <limits>
#include <queue>
#include <utility>
#include <vector>

struct DijkstraResult {
    std::vector<int> visitedOrder;
    std::vector<int> shortestPath;
    double totalDistance;
    int visitedCount;
};

DijkstraResult dijkstra(const std::vector<std::vector<std::pair<int, double>>>& graph,
                        int start,
                        int target) {
    const int n = static_cast<int>(graph.size());
    const double INF = std::numeric_limits<double>::infinity();

    std::vector<double> dist(n, INF);
    std::vector<int> previous(n, -1);
    std::vector<bool> settled(n, false);
    std::vector<int> visitedOrder;

    using State = std::pair<double, int>; // (distance, node)
    std::priority_queue<State, std::vector<State>, std::greater<State>> pq;

    dist[start] = 0.0;
    pq.push({0.0, start});

    while (!pq.empty()) {
        auto [curDist, u] = pq.top();
        pq.pop();

        if (settled[u]) {
            continue;
        }
        settled[u] = true;
        visitedOrder.push_back(u);

        if (u == target) {
            break;
        }

        for (const auto& [v, weight] : graph[u]) {
            if (weight < 0.0) {
                continue; // Dijkstra requires non-negative edge weights.
            }

            if (!settled[v] && curDist + weight < dist[v]) {
                dist[v] = curDist + weight;
                previous[v] = u;
                pq.push({dist[v], v});
            }
        }
    }

    std::vector<int> path;
    if (dist[target] != INF) {
        for (int at = target; at != -1; at = previous[at]) {
            path.push_back(at);
        }
        std::reverse(path.begin(), path.end());
    }

    return {
        visitedOrder,
        path,
        dist[target],
        static_cast<int>(visitedOrder.size())
    };
}

// Demo entry point; compile with -DPATHFINDING_DEMO_MAIN to run this file directly.
#ifdef PATHFINDING_DEMO_MAIN
int main() {
    // Example graph: graph[u] = { {v, weight}, ... }
    std::vector<std::vector<std::pair<int, double>>> graph = {
        {{1, 4.0}, {2, 1.0}}, // 0
        {{3, 1.0}},           // 1
        {{1, 2.0}, {3, 5.0}}, // 2
        {}                    // 3
    };

    int start = 0;
    int target = 3;

    DijkstraResult result = dijkstra(graph, start, target);

    std::cout << "Visited order: ";
    for (int node : result.visitedOrder) {
        std::cout << node << ' ';
    }
    std::cout << "\nShortest path: ";
    for (int node : result.shortestPath) {
        std::cout << node << ' ';
    }
    std::cout << "\nTotal distance: " << result.totalDistance;
    std::cout << "\nVisited nodes: " << result.visitedCount << '\n';

    return 0;
}
#endif  // PATHFINDING_DEMO_MAIN
