#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

struct PathfindingResult {
    std::string algorithm;
    std::pair<double, double> start;
    std::pair<double, double> end;
    std::vector<std::pair<double, double>> visited_order;
    std::vector<std::pair<double, double>> final_path;
    double total_distance;
    std::size_t nodes_visited;
};

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

void writeCoordinateArray(std::ofstream& out,
                          const std::vector<std::pair<double, double>>& coords,
                          int indentLevel) {
    const std::string indent(indentLevel, ' ');
    for (std::size_t i = 0; i < coords.size(); ++i) {
        out << indent << "[" << coords[i].first << ", " << coords[i].second << "]";
        if (i + 1 < coords.size()) {
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
    out << "  \"start\": [" << result.start.first << ", " << result.start.second << "],\n";
    out << "  \"end\": [" << result.end.first << ", " << result.end.second << "],\n";

    out << "  \"visited_order\": [\n";
    writeCoordinateArray(out, result.visited_order, 4);
    out << "  ],\n";

    out << "  \"final_path\": [\n";
    writeCoordinateArray(out, result.final_path, 4);
    out << "  ],\n";

    out << "  \"total_distance\": " << result.total_distance << ",\n";
    out << "  \"nodes_visited\": " << result.nodes_visited << "\n";
    out << "}\n";

    return out.good();
}

int main() {
    PathfindingResult result;
    result.algorithm = "A*";
    result.start = {37.774900, -122.419400};
    result.end = {37.784000, -122.409000};
    result.visited_order = {
        {37.774900, -122.419400},
        {37.776100, -122.417500},
        {37.778300, -122.415000},
        {37.781000, -122.412000},
        {37.784000, -122.409000}
    };
    result.final_path = {
        {37.774900, -122.419400},
        {37.778300, -122.415000},
        {37.784000, -122.409000}
    };
    result.total_distance = 1.642500;
    result.nodes_visited = result.visited_order.size();

    const std::string outputFile = "pathfinding_result.json";
    if (!writePathfindingResultToJson(result, outputFile)) {
        std::cerr << "Failed to write JSON output to: " << outputFile << "\n";
        return 1;
    }

    std::cout << "Pathfinding result written to " << outputFile << "\n";
    return 0;
}
