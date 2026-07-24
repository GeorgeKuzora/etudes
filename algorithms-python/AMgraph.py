from dataclasses import dataclass


@dataclass
class Graph:
    edges: list[list[int]]


def bfs(graph: Graph, source: int, needle: int):
    seen: list = []
    prev: dict = {source: -1}

    seen.append(source)  # id of initial node
    q: list = [source]
    curr = source

    while len(q):
        curr: int = q.pop(0)
        if curr == needle:
            break
        adjs = graph.edges[curr]
        for i in range(len(adjs)):
            if adjs[i] == 0:
                continue
            if i in seen:
                continue

            seen.append(i)
            prev[i] = curr
            q.append(i)

    out: list = []

    while prev[curr] != -1:
        out.append(curr)
        curr = prev[curr]

    if len(out):
        out.append(source)
        out.reverse()
        return out
    print("test")


if __name__ == "__main__":
    g = [
        [0, 7, 5, 0, 0],
        [0, 0, 0, 2, 0],
        [2, 1, 0, 5, 0],
        [0, 0, 0, 0, 6],
        [0, 0, 0, 0, 0],
    ]

    graph = Graph(edges=g)
    source = 0
    needle = 4

    print(bfs(graph, source, needle))
