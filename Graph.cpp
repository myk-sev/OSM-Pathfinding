#include "Graph.h"

Graph::EdgeList::Node::Node(const Edge& edge, Node* nextNode)
    : data(edge), next(nextNode) {}

Graph::EdgeList::EdgeList() : head_(nullptr) {}

Graph::EdgeList::EdgeList(const EdgeList& other) : head_(nullptr) {
    copyFrom(other);
}

Graph::EdgeList& Graph::EdgeList::operator=(const EdgeList& other) {
    if (this != &other) {
        clear();
        copyFrom(other);
    }
    return *this;
}

Graph::EdgeList::~EdgeList() {
    clear();
}

void Graph::EdgeList::pushFront(const Edge& edge) {
    head_ = new Node(edge, head_);
}

std::vector<Graph::Edge> Graph::EdgeList::toVector() const {
    std::vector<Graph::Edge> result;
    for (Node* current = head_; current != nullptr; current = current->next) {
        result.push_back(current->data);
    }
    return result;
}

void Graph::EdgeList::clear() {
    Node* current = head_;
    while (current != nullptr) {
        Node* next = current->next;
        delete current;
        current = next;
    }
    head_ = nullptr;
}

void Graph::EdgeList::copyFrom(const EdgeList& other) {
    if (other.head_ == nullptr) {
        return;
    }

    head_ = new Node(other.head_->data, nullptr);
    Node* destCurrent = head_;
    for (Node* srcCurrent = other.head_->next; srcCurrent != nullptr; srcCurrent = srcCurrent->next) {
        destCurrent->next = new Node(srcCurrent->data, nullptr);
        destCurrent = destCurrent->next;
    }
}

Graph::Graph(std::size_t vertexCount)
    : vertexCount_(vertexCount), adjacency_(nullptr) {
    adjacency_ = new EdgeList[vertexCount_];
}

Graph::Graph(const Graph& other)
    : vertexCount_(other.vertexCount_), adjacency_(nullptr) {
    adjacency_ = new EdgeList[vertexCount_];
    for (std::size_t i = 0; i < vertexCount_; ++i) {
        adjacency_[i] = other.adjacency_[i];
    }
}

Graph& Graph::operator=(const Graph& other) {
    if (this != &other) {
        EdgeList* newAdjacency = new EdgeList[other.vertexCount_];
        for (std::size_t i = 0; i < other.vertexCount_; ++i) {
            newAdjacency[i] = other.adjacency_[i];
        }

        delete[] adjacency_;
        adjacency_ = newAdjacency;
        vertexCount_ = other.vertexCount_;
    }
    return *this;
}

Graph::~Graph() {
    delete[] adjacency_;
}

void Graph::addEdge(std::size_t from, std::size_t to, double weight) {
    validateVertex(from);
    validateVertex(to);
    adjacency_[from].pushFront(Edge{to, weight});
}

std::vector<Graph::Edge> Graph::neighbors(std::size_t vertex) const {
    validateVertex(vertex);
    return adjacency_[vertex].toVector();
}

std::size_t Graph::size() const {
    return vertexCount_;
}

void Graph::validateVertex(std::size_t vertex) const {
    if (vertex >= vertexCount_) {
        throw std::out_of_range("Vertex index out of range");
    }
}
