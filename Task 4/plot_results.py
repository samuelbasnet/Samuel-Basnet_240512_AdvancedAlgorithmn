import csv
import matplotlib.pyplot as plt

with open("task4_results.csv") as f:
    rows = list(csv.DictReader(f))

ns = [int(r["n_items"]) for r in rows]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# Solution quality (bins needed - lower is better)
axes[0].plot(ns, [float(r["next_fit_bins_avg"]) for r in rows], "o-", label="Next-Fit (weak baseline)")
axes[0].plot(ns, [float(r["ffd_bins_avg"]) for r in rows], "s-", label="First-Fit Decreasing (greedy)")
axes[0].plot(ns, [float(r["local_search_bins_avg"]) for r in rows], "^-", label="Local search (from Next-Fit)")
axes[0].plot(ns, [float(r["sa_bins_avg"]) for r in rows], "d-", label="Simulated Annealing (from Next-Fit)")
axes[0].set_title("Solution quality: bins needed (lower is better)")
axes[0].set_xlabel("Number of items")
axes[0].set_ylabel("Average bins used")
axes[0].legend()
axes[0].grid(alpha=0.3)

# Runtime (log scale since SA is orders of magnitude slower)
axes[1].plot(ns, [float(r["next_fit_time"]) for r in rows], "o-", label="Next-Fit")
axes[1].plot(ns, [float(r["ffd_time"]) for r in rows], "s-", label="First-Fit Decreasing")
axes[1].plot(ns, [float(r["local_search_time"]) for r in rows], "^-", label="Local search")
axes[1].plot(ns, [float(r["sa_time"]) for r in rows], "d-", label="Simulated Annealing")
axes[1].set_yscale("log")
axes[1].set_title("Runtime (log scale)")
axes[1].set_xlabel("Number of items")
axes[1].set_ylabel("Time (seconds, log scale)")
axes[1].legend()
axes[1].grid(alpha=0.3, which="both")

plt.tight_layout()
plt.savefig("task4_comparison.png", dpi=150)
print("Saved task4_comparison.png")
