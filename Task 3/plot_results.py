import csv
import matplotlib.pyplot as plt

# --- DP vs Brute Force ---
with open("task3_dp_results.csv") as f:
    dp_rows = list(csv.DictReader(f))

fig, ax = plt.subplots(figsize=(6.5, 4.5))
ns = [int(r["n"]) for r in dp_rows]
dp_times = [float(r["dp_time"]) for r in dp_rows]
bf_times = [float(r["brute_force_time"]) if r["brute_force_time"] not in (None, "", "None") else None for r in dp_rows]

ax.plot(ns, dp_times, "o-", label="DP (O(n log n))")
bf_ns = [n for n, t in zip(ns, bf_times) if t is not None]
bf_vals = [t for t in bf_times if t is not None]
ax.plot(bf_ns, bf_vals, "s-", label="Brute force (O(2^n))")
ax.set_yscale("log")
ax.set_title("Weighted Job Scheduling: DP vs Brute Force")
ax.set_xlabel("Number of jobs (n)")
ax.set_ylabel("Time (seconds, log scale)")
ax.legend()
ax.grid(alpha=0.3, which="both")
plt.tight_layout()
plt.savefig("task3_dp_vs_bruteforce.png", dpi=150)
print("Saved task3_dp_vs_bruteforce.png")

# --- Greedy scaling ---
with open("task3_greedy_results.csv") as f:
    greedy_rows = list(csv.DictReader(f))

fig2, ax2 = plt.subplots(figsize=(6.5, 4.5))
ns2 = [int(r["n"]) for r in greedy_rows]
greedy_times = [float(r["greedy_time"]) for r in greedy_rows]
ax2.plot(ns2, greedy_times, "o-", color="green", label="Greedy sweep O(n log n)")
ax2.set_title("Minimum Platforms: Greedy scaling")
ax2.set_xlabel("Number of trains (n)")
ax2.set_ylabel("Time (seconds)")
ax2.legend()
ax2.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("task3_greedy_scaling.png", dpi=150)
print("Saved task3_greedy_scaling.png")

# --- Backtracking: pruning impact (log scale on nodes explored) ---
with open("task3_backtracking_results.csv") as f:
    bt_rows = list(csv.DictReader(f))

fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 4.5))

ns3 = [int(r["n"]) for r in bt_rows]
warns_nodes = [int(r["warnsdorff_nodes"]) for r in bt_rows]
ax3a.plot(ns3, warns_nodes, "o-", label="With Warnsdorff pruning")

no_prune_ns = [int(r["n"]) for r in bt_rows if r["no_pruning_nodes"] not in (None, "", "None")]
no_prune_nodes = [int(r["no_pruning_nodes"]) for r in bt_rows if r["no_pruning_nodes"] not in (None, "", "None")]
ax3a.plot(no_prune_ns, no_prune_nodes, "s-", label="No pruning heuristic")
ax3a.set_yscale("log")
ax3a.set_title("Knight's Tour: nodes explored")
ax3a.set_xlabel("Board size n (n x n)")
ax3a.set_ylabel("Nodes explored (log scale)")
ax3a.legend()
ax3a.grid(alpha=0.3, which="both")

warns_time = [float(r["warnsdorff_time"]) for r in bt_rows]
ax3b.plot(ns3, warns_time, "o-", label="With Warnsdorff pruning")
no_prune_time = [float(r["no_pruning_time"]) for r in bt_rows if r["no_pruning_time"] not in (None, "", "None")]
ax3b.plot(no_prune_ns, no_prune_time, "s-", label="No pruning heuristic")
ax3b.set_yscale("log")
ax3b.set_title("Knight's Tour: runtime")
ax3b.set_xlabel("Board size n (n x n)")
ax3b.set_ylabel("Time seconds (log scale)")
ax3b.legend()
ax3b.grid(alpha=0.3, which="both")

plt.tight_layout()
plt.savefig("task3_backtracking_pruning.png", dpi=150)
print("Saved task3_backtracking_pruning.png")
