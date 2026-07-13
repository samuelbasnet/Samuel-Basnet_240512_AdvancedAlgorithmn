"""
Task 2: Empirical comparison of Dijkstra, Prim, Bellman-Ford.
Tests on sparse and dense random graphs of increasing size.
"""

import time
import random
import csv
from graph_algorithms import Graph, dijkstra, prim_mst, bellman_ford


def make_random_graph(n_nodes, density, seed=0, allow_negative=False):
    random.seed(seed)
    g = Graph(directed=True)
    nodes = [f"N{i}" for i in range(n_nodes)]
    for node in nodes:
        g.add_node(node)

    max_edges = n_nodes * (n_nodes - 1)
    n_edges = int(max_edges * density)

    # Ensure connectivity: a random spanning path first
    shuffled = nodes[:]
    random.shuffle(shuffled)
    for i in range(len(shuffled) - 1):
        w = random.randint(1, 20)
        g.add_edge(shuffled[i], shuffled[i + 1], w)

    added = len(shuffled) - 1
    attempts = 0
    while added < n_edges and attempts < n_edges * 5:
        u, v = random.choice(nodes), random.choice(nodes)
        attempts += 1
        if u == v:
            continue
        w = random.randint(1, 20)
        if allow_negative and random.random() < 0.05:
            w = -random.randint(1, 5)
        g.add_edge(u, v, w)
        added += 1

    return g, nodes


def time_fn(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return time.perf_counter() - start, result


def run_benchmark():
    sizes = [50, 100, 300, 500]
    results = []

    for n in sizes:
        for density_name, density in [("sparse", 0.02), ("dense", 0.3)]:
            g, nodes = make_random_graph(n, density, seed=n)
            source = nodes[0]

            t_dijkstra, _ = time_fn(dijkstra, g, source)
            t_prim, _ = time_fn(prim_mst, g)
            t_bf, _ = time_fn(bellman_ford, g, source)

            row = {
                "n_nodes": n,
                "density": density_name,
                "n_edges": g.num_edges(),
                "dijkstra_time": t_dijkstra,
                "prim_time": t_prim,
                "bellman_ford_time": t_bf,
            }
            results.append(row)
            print(f"n={n:>4} ({density_name:6s}, E={g.num_edges():>5})  "
                  f"Dijkstra={t_dijkstra:.5f}s  Prim={t_prim:.5f}s  Bellman-Ford={t_bf:.5f}s")

    with open("task2_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
        writer.writeheader()
        writer.writerows(results)
    print("\nSaved task2_results.csv")
    return results


if __name__ == "__main__":
    run_benchmark()
