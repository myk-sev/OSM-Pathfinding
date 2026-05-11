#ifndef GRAPH_H
#define GRAPH_H

#include <cstddef>
#include <stdexcept>
#include <utility>
#include <vector>

class Graph {
public:
    struct Edge {
        std::size_t to;
        double weight;
    };

    explicit Graph(std::size_t vertexCount = 0);
    Graph(const Graph& other);
    Graph& operator=(const Graph& other);
    ~Graph();

    void addEdge(std::size_t from, std::size_t to, double weight);
    std::vector<Edge> neighbors(std::size_t vertex) const;
    std::size_t size() const;

private:
    class EdgeList {
    public:
        EdgeList();
        EdgeList(const EdgeList& other);
        EdgeList& operator=(const EdgeList& other);
        ~EdgeList();

        void pushFront(const Edge& edge);
        std::vector<Edge> toVector() const;

    private:
        struct Node {
            Edge data;
            Node* next;

            Node(const Edge& edge, Node* nextNode);
        };

        Node* head_;

        void clear();
        void copyFrom(const EdgeList& other);
    };

    std::size_t vertexCount_;
    EdgeList* adjacency_;

    void validateVertex(std::size_t vertex) const;
};

#endif
