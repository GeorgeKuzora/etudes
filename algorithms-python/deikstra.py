from dataclasses import dataclass


@dataclass
class Edge:
    to: int
    weight: int


@dataclass
class Graph:
    edges: list[list[Edge]]
    nodes: list[int]


infinity = float("inf")


def has_unvisited(seen: list, dist: list) -> bool:
    for i in range(len(seen)):
        if not seen[i] and dist[i] < infinity:
            return True
    return False


def get_lowest_unvisited(seen: list, dist: list):
    id = -1
    lowest_distance = infinity
    for i in range(len(seen)):
        if seen[i]:
            continue
        if lowest_distance > dist[i]:
            lowest_distance = dist[i]
            id = i
    return id


def deikstraAlgorithm(graph: Graph, source: int, needle: int):
    seen = []
    dist = []
    prev = []
    curr = source
    for i in graph.nodes:
        seen.append(False)
        dist.append(infinity)
        prev.append(-1)
    dist[source] = 0
    while has_unvisited(seen, dist):
        curr = get_lowest_unvisited(seen, dist)
        print(curr)
        seen[curr] = True
        if curr == needle:
            break
        adjs = graph.edges[curr]
        for i in range(len(adjs)):
            edge = adjs[i]
            if seen[edge.to]:
                continue
            d = dist[curr] + edge.weight
            if d < dist[edge.to]:
                dist[edge.to] = d
                prev[edge.to] = curr

    out: list = []

    while prev[curr] != -1:
        out.append(curr)
        curr = prev[curr]
    if len(out):
        out.append(source)
        out.reverse()
    return out


if __name__ == "__main__":
    nodes = [0, 1, 2, 3, 4]
    edges = [
        [
            Edge(1, 2),
            Edge(2, 4),
        ],
        [
            Edge(2, 3),
            Edge(3, 7),
        ],
        [
            Edge(3, 1),
        ],
        [
            Edge(4, 1),
        ],
        [],
    ]

    graph = Graph(nodes=nodes, edges=edges)
    source = 0
    needle = 4
    print(deikstraAlgorithm(graph, source, needle))
