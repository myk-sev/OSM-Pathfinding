#include <fstream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

struct Node {
    long long id;
    double latitude;
    double longitude;
};

struct Edge {
    long long from;
    long long to;
    double weight;
};

struct GraphInput {
    std::vector<Node> nodes;
    std::vector<Edge> edges;
    long long start_id;
    long long end_id;
};

[[noreturn]] void ThrowLineError(int line_number, const std::string& message) {
    std::ostringstream oss;
    oss << "Invalid graph file at line " << line_number << ": " << message;
    throw std::runtime_error(oss.str());
}

GraphInput ReadGraphInputFile(const std::string& path) {
    std::ifstream in(path);
    if (!in.is_open()) {
        throw std::runtime_error("Unable to open graph file: " + path);
    }

    GraphInput result;
    std::unordered_map<long long, bool> node_ids;

    std::string line;
    int line_number = 0;

    if (!std::getline(in, line)) {
        throw std::runtime_error("Graph file is empty; expected NODE_COUNT EDGE_COUNT on line 1");
    }
    ++line_number;

    std::istringstream header(line);
    long long node_count = -1;
    long long edge_count = -1;
    std::string extra;
    if (!(header >> node_count >> edge_count) || (header >> extra)) {
        ThrowLineError(line_number, "expected exactly two integers: NODE_COUNT EDGE_COUNT");
    }
    if (node_count < 0 || edge_count < 0) {
        ThrowLineError(line_number, "NODE_COUNT and EDGE_COUNT must be non-negative");
    }

    result.nodes.reserve(static_cast<size_t>(node_count));
    result.edges.reserve(static_cast<size_t>(edge_count));

    for (long long i = 0; i < node_count; ++i) {
        if (!std::getline(in, line)) {
            throw std::runtime_error("Unexpected end of file while reading node rows");
        }
        ++line_number;

        std::istringstream node_line(line);
        Node node{};
        if (!(node_line >> node.id >> node.latitude >> node.longitude) || (node_line >> extra)) {
            ThrowLineError(line_number, "expected: node_id latitude longitude");
        }
        if (node_ids.count(node.id)) {
            ThrowLineError(line_number, "duplicate node_id: " + std::to_string(node.id));
        }
        node_ids[node.id] = true;
        result.nodes.push_back(node);
    }

    if (!std::getline(in, line)) {
        throw std::runtime_error("Unexpected end of file; expected EDGE marker");
    }
    ++line_number;
    if (line != "EDGE") {
        ThrowLineError(line_number, "expected EDGE marker");
    }

    for (long long i = 0; i < edge_count; ++i) {
        if (!std::getline(in, line)) {
            throw std::runtime_error("Unexpected end of file while reading edge rows");
        }
        ++line_number;

        std::istringstream edge_line(line);
        Edge edge{};
        if (!(edge_line >> edge.from >> edge.to >> edge.weight) || (edge_line >> extra)) {
            ThrowLineError(line_number, "expected: from_id to_id weight");
        }
        if (!node_ids.count(edge.from)) {
            ThrowLineError(line_number, "edge from_id not found in node list: " + std::to_string(edge.from));
        }
        if (!node_ids.count(edge.to)) {
            ThrowLineError(line_number, "edge to_id not found in node list: " + std::to_string(edge.to));
        }
        result.edges.push_back(edge);
    }

    if (!std::getline(in, line)) {
        throw std::runtime_error("Unexpected end of file; expected START_END marker");
    }
    ++line_number;
    if (line != "START_END") {
        ThrowLineError(line_number, "expected START_END marker");
    }

    if (!std::getline(in, line)) {
        throw std::runtime_error("Unexpected end of file; expected start_id end_id row");
    }
    ++line_number;

    std::istringstream start_end_line(line);
    if (!(start_end_line >> result.start_id >> result.end_id) || (start_end_line >> extra)) {
        ThrowLineError(line_number, "expected: start_id end_id");
    }
    if (!node_ids.count(result.start_id)) {
        ThrowLineError(line_number, "start_id not found in node list: " + std::to_string(result.start_id));
    }
    if (!node_ids.count(result.end_id)) {
        ThrowLineError(line_number, "end_id not found in node list: " + std::to_string(result.end_id));
    }

    if (std::getline(in, line)) {
        ++line_number;
        ThrowLineError(line_number, "unexpected extra content after start/end row");
    }

    return result;
}
