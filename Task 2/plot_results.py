import csv
import matplotlib.pyplot as plt
from graph_algorithms import Graph, dijkstra, prim_mst

with open("task2_results.csv") as f:
    rows = list(csv.DictReader(f))

sparse = [r for r in rows if r["density"] == "sparse"]
dense = [r for r in rows if r["density"] == "dense"]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

for ax, data, title in [(axes[0], sparse, "Sparse graphs (density=0.02)"),
                         (axes[1], dense, "Dense graphs (density=0.3)")]:
    ns = [int(r["n_nodes"]) for r in data]
    ax.plot(ns, [float(r["dijkstra_time"]) for r in data], "o-", label="Dijkstra")
    ax.plot(ns, [float(r["prim_time"]) for r in data], "s-", label="Prim")
    ax.plot(ns, [float(r["bellman_ford_time"]) for r in data], "^-", label="Bellman-Ford")
    ax.set_title(title)
    ax.set_xlabel("Number of nodes (V)")
    ax.set_ylabel("Time (seconds)")
    ax.legend()
    ax.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("task2_comparison.png", dpi=150)
print("Saved task2_comparison.png")

# --- Step-by-step visualisation of Dijkstra's shortest path tree construction ---
g = Graph(directed=True)
edges = [("A", "B", 4), ("A", "C", 1), ("C", "B", 2), ("B", "D", 1),
         ("C", "D", 5), ("D", "E", 3), ("C", "E", 8), ("B", "E", 6)]
for u, v, w in edges:
    g.add_edge(u, v, w)

dist, prev, steps = dijkstra(g, "A")

fig2, ax2 = plt.subplots(figsize=(6, 4.5))
ax2.bar(steps, [dist[n] for n in steps], color="steelblue")
ax2.set_title("Dijkstra: order nodes finalised & shortest distance from A")
ax2.set_xlabel("Node (in order finalised)")
ax2.set_ylabel("Shortest distance from A")
for i, n in enumerate(steps):
    ax2.text(i, dist[n] + 0.1, str(dist[n]), ha="center")
plt.tight_layout()
plt.savefig("task2_dijkstra_steps.png", dpi=150)
print("Saved task2_dijkstra_steps.png")
