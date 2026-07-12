"""
Task 2: Graph Algorithms and Pathfinding for a transportation network.

Graph representation: weighted directed graph via adjacency list
(dict of node -> list of (neighbour, weight)). Adjacency list chosen over
adjacency matrix because real transportation networks are sparse
(each city connects to only a handful of others, not all cities), giving
O(V+E) space instead of O(V^2), and O(E) edge iteration instead of O(V^2).
"""

import heapq
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class Graph:
    def __init__(self, directed: bool = True):
        self.directed = directed
        self.adj: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        self.nodes = set()

    def add_edge(self, u: str, v: str, w: float) -> None:
        self.adj[u].append((v, w))
        self.nodes.add(u)
        self.nodes.add(v)
        if not self.directed:
            self.adj[v].append((u, w))

    def add_node(self, u: str) -> None:
        self.nodes.add(u)
        if u not in self.adj:
            self.adj[u] = []

    def edges(self):
        for u, lst in self.adj.items():
            for v, w in lst:
                yield u, v, w

    def num_edges(self) -> int:
        return sum(len(v) for v in self.adj.values())

    def num_nodes(self) -> int:
        return len(self.nodes)


# ---------------------------------------------------------------------------
# Dijkstra's algorithm (single-source shortest path, non-negative weights)
# Time: O((V + E) log V) with a binary heap
# ---------------------------------------------------------------------------
def dijkstra(graph: Graph, source: str):
    dist = {n: float("inf") for n in graph.nodes}
    prev = {n: None for n in graph.nodes}
    dist[source] = 0
    pq = [(0, source)]
    visited = set()
    steps = []  # record order nodes are finalised, for visualisation

    while pq:
        d, u = heapq.heappop(pq)
        if u in visited:
            continue
        visited.add(u)
        steps.append(u)
        for v, w in graph.adj[u]:
            if w < 0:
                raise ValueError("Dijkstra does not support negative edge weights")
            nd = d + w
            if nd < dist[v]:
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))

    return dist, prev, steps


def reconstruct_path(prev, target):
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = prev[node]
    return list(reversed(path))


# ---------------------------------------------------------------------------
# Prim's algorithm (Minimum Spanning Tree) - treats graph as undirected
# Time: O((V + E) log V) with a binary heap
# ---------------------------------------------------------------------------
def prim_mst(graph: Graph, start: Optional[str] = None):
    if not graph.nodes:
        return [], 0.0

    # Build undirected adjacency (MST requires undirected graph)
    undirected = defaultdict(list)
    for u, v, w in graph.edges():
        undirected[u].append((v, w))
        undirected[v].append((u, w))

    start = start or next(iter(graph.nodes))
    visited = {start}
    edges_heap = [(w, start, v) for v, w in undirected[start]]
    heapq.heapify(edges_heap)
    mst_edges = []
    total_weight = 0.0
    build_steps = []  # for visualisation of MST construction order

    while edges_heap and len(visited) < len(graph.nodes):
        w, u, v = heapq.heappop(edges_heap)
        if v in visited:
            continue
        visited.add(v)
        mst_edges.append((u, v, w))
        build_steps.append((u, v, w))
        total_weight += w
        for nxt, nw in undirected[v]:
            if nxt not in visited:
                heapq.heappush(edges_heap, (nw, v, nxt))

    return mst_edges, total_weight, build_steps


# ---------------------------------------------------------------------------
# Bellman-Ford algorithm - handles negative weights, detects negative cycles
# Time: O(V * E)
# ---------------------------------------------------------------------------
def bellman_ford(graph: Graph, source: str):
    dist = {n: float("inf") for n in graph.nodes}
    prev = {n: None for n in graph.nodes}
    dist[source] = 0
    edge_list = list(graph.edges())

    for i in range(len(graph.nodes) - 1):
        updated = False
        for u, v, w in edge_list:
            if dist[u] != float("inf") and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                prev[v] = u
                updated = True
        if not updated:
            break  # early termination if converged

    # Detect negative-weight cycles: one more relaxation pass
    negative_cycle_nodes = set()
    for u, v, w in edge_list:
        if dist[u] != float("inf") and dist[u] + w < dist[v]:
            negative_cycle_nodes.add(v)

    has_negative_cycle = len(negative_cycle_nodes) > 0
    return dist, prev, has_negative_cycle, negative_cycle_nodes
