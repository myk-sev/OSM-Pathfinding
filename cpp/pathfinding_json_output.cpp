#include <algorithm>
#include <cctype>
#include <cmath>
#include <fstream>
#include <functional>
#include <iomanip>
#include <iostream>
#include <limits>
#include <queue>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>

struct Node {
    int id;
    double latitude;
    double longitude;
};

struct Edge {
    int from;
    int to;
    double weight;
};

struct GraphInput {
    std::vector<Node> nodes;
    std::vector<Edge> edges;
    int start_id;
    int end_id;
};

struct PathfindingResult {
    std::string algorithm;
    int start;
    int end;
    std::vector<int> visited_order;
    std::vector<int> final_path;
    double total_distance;
    std::size_t nodes_visited;
};

using Adjacency = std::unordered_map<int, std::vector<std::pair<int, double>>>;

Adjacency buildAdjacency(const std::vector<Edge>& edges) {
    Adjacency graph;
    for (const Edge& edge : edges) {
        graph[edge.from].push_back({edge.to, edge.weight});
    }
    return graph;
}

std::vector<int> reconstructPath(const std::unordered_map<int, int>& previous,
                                 int start,
                                 int end) {
    if (start == end) {
        return {start};
    }
    if (!previous.count(end)) {
        return {};
    }

    std::vector<int> path;
    for (int at = end;; at = previous.at(at)) {
        path.push_back(at);
        if (at == start) {
            break;
        }
    }
    std::reverse(path.begin(), path.end());
    return path;
}

double pathDistance(const std::vector<Edge>& edges, const std::vector<int>& path) {
    if (path.empty()) {
        return std::numeric_limits<double>::infinity();
    }

    std::unordered_map<int, std::unordered_map<int, double>> weights;
    for (const Edge& edge : edges) {
        auto& targets = weights[edge.from];
        const auto existing = targets.find(edge.to);
        if (existing == targets.end() || edge.weight < existing->second) {
            targets[edge.to] = edge.weight;
        }
    }

    double total = 0.0;
    for (std::size_t i = 0; i + 1 < path.size(); ++i) {
        const int from = path[i];
        const int to = path[i + 1];
        if (!weights.count(from) || !weights[from].count(to)) {
            return std::numeric_limits<double>::infinity();
        }
        total += weights[from][to];
    }
    return total;
}

PathfindingResult makeResultShell(const GraphInput& input, const std::string& algorithm) {
    PathfindingResult result;
    result.algorithm = algorithm;
    result.start = input.start_id;
    result.end = input.end_id;
    result.total_distance = std::numeric_limits<double>::infinity();
    result.nodes_visited = 0;
    return result;
}

std::string escapeJson(const std::string& input) {
    std::ostringstream escaped;
    for (char ch : input) {
        switch (ch) {
            case '"': escaped << "\\\""; break;
            case '\\': escaped << "\\\\"; break;
            case '\b': escaped << "\\b"; break;
            case '\f': escaped << "\\f"; break;
            case '\n': escaped << "\\n"; break;
            case '\r': escaped << "\\r"; break;
            case '\t': escaped << "\\t"; break;
            default:
                if (static_cast<unsigned char>(ch) < 0x20) {
                    escaped << "\\u"
                            << std::hex << std::setw(4) << std::setfill('0')
                            << static_cast<int>(static_cast<unsigned char>(ch))
                            << std::dec;
                } else {
                    escaped << ch;
                }
        }
    }
    return escaped.str();
}

void writeIntegerArray(std::ofstream& out,
                       const std::vector<int>& values,
                       int indentLevel) {
    const std::string indent(indentLevel, ' ');
    for (std::size_t i = 0; i < values.size(); ++i) {
        out << indent << values[i];
        if (i + 1 < values.size()) {
            out << ",";
        }
        out << "\n";
    }
}

bool writePathfindingResultToJson(const PathfindingResult& result,
                                  const std::string& fileName) {
    std::ofstream out(fileName);
    if (!out.is_open()) {
        return false;
    }

    out << std::fixed << std::setprecision(6);
    out << "{\n";
    out << "  \"algorithm\": \"" << escapeJson(result.algorithm) << "\",\n";
    out << "  \"start\": " << result.start << ",\n";
    out << "  \"end\": " << result.end << ",\n";

    out << "  \"visited_order\": [\n";
    writeIntegerArray(out, result.visited_order, 4);
    out << "  ],\n";

    out << "  \"final_path\": [\n";
    writeIntegerArray(out, result.final_path, 4);
    out << "  ],\n";

    if (std::isfinite(result.total_distance)) {
        out << "  \"total_distance\": " << result.total_distance << ",\n";
    } else {
        out << "  \"total_distance\": null,\n";
    }
    out << "  \"nodes_visited\": " << result.nodes_visited << "\n";
    out << "}\n";

    return out.good();
}

bool readDataLine(std::ifstream& in, std::string& line) {
    while (std::getline(in, line)) {
        if (!line.empty() && line[0] != '#') {
            return true;
        }
    }
    return false;
}

GraphInput readGraphInput(const std::string& fileName) {
    std::ifstream in(fileName);
    if (!in.is_open()) {
        throw std::runtime_error("Unable to open input file: " + fileName);
    }

    std::string line;
    if (!readDataLine(in, line)) {
        throw std::runtime_error("Input file is empty");
    }

    std::istringstream header(line);
    int nodeCount = 0;
    int edgeCount = 0;
    if (!(header >> nodeCount >> edgeCount)) {
        throw std::runtime_error("Expected node and edge counts");
    }

    GraphInput input;
    input.nodes.reserve(nodeCount);
    input.edges.reserve(edgeCount);

    for (int i = 0; i < nodeCount; ++i) {
        if (!readDataLine(in, line)) {
            throw std::runtime_error("Unexpected end of file while reading nodes");
        }
        std::istringstream row(line);
        Node node{};
        if (!(row >> node.id >> node.latitude >> node.longitude)) {
            throw std::runtime_error("Invalid node row: " + line);
        }
        input.nodes.push_back(node);
    }

    for (int i = 0; i < edgeCount; ++i) {
        if (!readDataLine(in, line)) {
            throw std::runtime_error("Unexpected end of file while reading edges");
        }
        std::istringstream row(line);
        Edge edge{};
        if (!(row >> edge.from >> edge.to >> edge.weight)) {
            throw std::runtime_error("Invalid edge row: " + line);
        }
        input.edges.push_back(edge);
    }

    if (!readDataLine(in, line) || line != "START_END") {
        throw std::runtime_error("Expected START_END marker");
    }
    if (!readDataLine(in, line)) {
        throw std::runtime_error("Missing start/end row");
    }

    std::istringstream startEnd(line);
    if (!(startEnd >> input.start_id >> input.end_id)) {
        throw std::runtime_error("Invalid start/end row: " + line);
    }

    return input;
}

PathfindingResult runDijkstra(const GraphInput& input, const std::string& algorithm) {
    Adjacency graph = buildAdjacency(input.edges);

    std::unordered_map<int, double> distance;
    std::unordered_map<int, int> previous;
    std::unordered_set<int> settled;
    using State = std::pair<double, int>;
    std::priority_queue<State, std::vector<State>, std::greater<State>> frontier;

    distance[input.start_id] = 0.0;
    frontier.push({0.0, input.start_id});

    PathfindingResult result = makeResultShell(input, algorithm);

    while (!frontier.empty()) {
        auto [currentDistance, node] = frontier.top();
        frontier.pop();

        if (settled.count(node)) {
            continue;
        }
        settled.insert(node);
        result.visited_order.push_back(node);

        if (node == input.end_id) {
            break;
        }

        for (const auto& [neighbor, weight] : graph[node]) {
            if (settled.count(neighbor) || weight < 0.0) {
                continue;
            }
            const double candidate = currentDistance + weight;
            if (!distance.count(neighbor) || candidate < distance[neighbor]) {
                distance[neighbor] = candidate;
                previous[neighbor] = node;
                frontier.push({candidate, neighbor});
            }
        }
    }

    if (distance.count(input.end_id)) {
        result.total_distance = distance[input.end_id];
        for (int at = input.end_id;; at = previous[at]) {
            result.final_path.push_back(at);
            if (at == input.start_id) {
                break;
            }
        }
        std::reverse(result.final_path.begin(), result.final_path.end());
    }

    result.nodes_visited = result.visited_order.size();
    return result;
}

PathfindingResult runDepthFirst(const GraphInput& input, const std::string& algorithm) {
    Adjacency graph = buildAdjacency(input.edges);
    std::unordered_map<int, int> previous;
    std::unordered_set<int> discovered;
    std::vector<int> stack;

    PathfindingResult result = makeResultShell(input, algorithm);
    discovered.insert(input.start_id);
    stack.push_back(input.start_id);

    while (!stack.empty()) {
        const int node = stack.back();
        stack.pop_back();
        result.visited_order.push_back(node);

        if (node == input.end_id) {
            break;
        }

        const auto it = graph.find(node);
        if (it == graph.end()) {
            continue;
        }

        const auto& neighbors = it->second;
        for (auto neighborIt = neighbors.rbegin(); neighborIt != neighbors.rend(); ++neighborIt) {
            const int neighbor = neighborIt->first;
            if (!discovered.count(neighbor)) {
                discovered.insert(neighbor);
                previous[neighbor] = node;
                stack.push_back(neighbor);
            }
        }
    }

    result.final_path = reconstructPath(previous, input.start_id, input.end_id);
    result.total_distance = pathDistance(input.edges, result.final_path);
    result.nodes_visited = result.visited_order.size();
    return result;
}

PathfindingResult runBreadthFirst(const GraphInput& input, const std::string& algorithm) {
    Adjacency graph = buildAdjacency(input.edges);
    std::unordered_map<int, int> previous;
    std::unordered_set<int> discovered;
    std::queue<int> frontier;

    PathfindingResult result = makeResultShell(input, algorithm);
    discovered.insert(input.start_id);
    frontier.push(input.start_id);

    while (!frontier.empty()) {
        const int node = frontier.front();
        frontier.pop();
        result.visited_order.push_back(node);

        if (node == input.end_id) {
            break;
        }

        for (const auto& [neighbor, weight] : graph[node]) {
            (void)weight;
            if (!discovered.count(neighbor)) {
                discovered.insert(neighbor);
                previous[neighbor] = node;
                frontier.push(neighbor);
            }
        }
    }

    result.final_path = reconstructPath(previous, input.start_id, input.end_id);
    result.total_distance = pathDistance(input.edges, result.final_path);
    result.nodes_visited = result.visited_order.size();
    return result;
}

std::string normalizeAlgorithm(std::string algorithm) {
    std::transform(algorithm.begin(), algorithm.end(), algorithm.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    std::replace(algorithm.begin(), algorithm.end(), '-', '_');

    if (algorithm == "depth_first" || algorithm == "depth_first_search") {
        return "dfs";
    }
    if (algorithm == "breadth_first" || algorithm == "breadth_first_search") {
        return "bfs";
    }
    if (algorithm == "djikstra" || algorithm == "djikstras" || algorithm == "dijkstras") {
        return "dijkstra";
    }
    if (algorithm == "dfs" || algorithm == "bfs") {
        return algorithm;
    }
    return "dijkstra";
}

PathfindingResult runPathfinder(const GraphInput& input, const std::string& algorithm) {
    const std::string selectedAlgorithm = normalizeAlgorithm(algorithm);
    if (selectedAlgorithm == "dfs") {
        return runDepthFirst(input, selectedAlgorithm);
    }
    if (selectedAlgorithm == "bfs") {
        return runBreadthFirst(input, selectedAlgorithm);
    }
    return runDijkstra(input, selectedAlgorithm);
}

int main(int argc, char* argv[]) {
    if (argc != 4) {
        std::cerr << "Usage: pathfinder <input_file> <output_file> <algorithm>\n";
        return 1;
    }

    const std::string inputFile = argv[1];
    const std::string outputFile = argv[2];
    const std::string algorithm = argv[3];

    PathfindingResult result;
    try {
        result = runPathfinder(readGraphInput(inputFile), algorithm);
    } catch (const std::exception& exc) {
        std::cerr << exc.what() << "\n";
        return 1;
    }

    if (!writePathfindingResultToJson(result, outputFile)) {
        std::cerr << "Failed to write JSON output to: " << outputFile << "\n";
        return 1;
    }

    std::cout << "Pathfinding result written to " << outputFile << "\n";
    return 0;
}
