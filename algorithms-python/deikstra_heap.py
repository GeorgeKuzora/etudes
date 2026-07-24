import heapq
from dataclasses import dataclass


@dataclass
class Edge:
    to: int
    weight: int


class Rand:
    def __init__(self) -> None:
        pass


class Randi:
    def __init__(self) -> None:
        pass


class Graph:
    def __init__(self, vertex_qnt: int) -> int:
        self.vertex_qnt = vertex_qnt
        self.edges: list[list[Edge]] = [[] for _ in range(self.vertex_qnt)]

    def addEdge(self, from_vertex: int, to_vertex: int, weight: int):
        self.edges[from_vertex].append(Edge(to=to_vertex, weight=weight))

    def dejkstra_shortest_path(self, source: int, needle: int) -> list[int]:
        curr = source
        dist: list = [float("inf")] * self.vertex_qnt
        dist[source] = 0
        priority_queue = []
        heapq.heappush(priority_queue, (0, source))
        prev = [-1] * self.vertex_qnt

        while priority_queue:
            distance, curr = heapq.heappop(priority_queue)
            if curr == needle:
                break

            for edge in self.edges[curr]:
                if dist[edge.to] > distance + edge.weight:
                    dist[edge.to] = distance + edge.weight
                    heapq.heappush(priority_queue, (dist[edge.to], edge.to))
                    prev[edge.to] = curr

        out = []
        while prev[curr] != -1:
            out.append(curr)
            curr = prev[curr]
        if len(out):
            out.append(source)
            out.reverse()
        return out


if __name__ == "__main__":
    V = 5
    g = Graph(V)

    g.addEdge(0, 1, 2)
    g.addEdge(0, 2, 6)
    g.addEdge(1, 2, 3)
    g.addEdge(1, 3, 7)
    g.addEdge(2, 3, 1)
    g.addEdge(3, 4, 1)
    g.addEdge(4, 4, 1)

    path = g.dejkstra_shortest_path(0, 4)
    print(path)
