from dataclasses import dataclass
from queue import Queue


@dataclass
class Graph:
    edges: list[list[int]]


def dfs(graph: Graph, source: int, needle: int) -> list:
    seen: list = []
    path: list = []
    walk(graph, source, needle, seen, path)
    return path


def walk(graph: Graph, curr: int, needle: int, seen: list, path: list) -> bool:
    if curr in seen:
        return False
    seen.append(curr)
    # pre
    path.append(curr)
    if curr == needle:
        return True
    # recurse
    for edge in graph.edges[curr]:
        if walk(graph, edge, needle, seen, path):
            return True
    # post
    path.pop()
    return False


def bfs(graph: Graph, source: int, needle: int) -> list:
    seen: list = []
    prev: dict = {}
    q: list = []
    curr = source
    prev[curr] = -1
    q.append(curr)
    seen.append(curr)
    while len(q):
        curr = q.pop(0)
        if curr == needle:
            break
        adjs = graph.edges[curr]
        for e in adjs:
            if e in seen:
                continue
            seen.append(e)
            prev[e] = curr
            q.append(e)
    out: list = []

    while prev[curr] != -1:
        out.append(curr)
        curr = prev[curr]
    if len(out):
        out.append(source)
        out.reverse()
    return out


def bfs_heap(graph: Graph, source: int, needle: int) -> list:
    pass


if __name__ == "__main__":
    g = [[1, 2], [3], [0, 1, 3], [4], []]

    graph = Graph(edges=g)
    source = 0
    needle = 4

    print("Depth first")
    print(dfs(graph, source, needle))
    print("Breath first")
    print(bfs(graph, source, needle))

    max(g)
