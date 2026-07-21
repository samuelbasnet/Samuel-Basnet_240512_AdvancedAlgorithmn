import csv
import matplotlib.pyplot as plt

with open("task5_results.csv") as f:
    rows = list(csv.DictReader(f))

thread_counts = [1, 2, 4, 8]
fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

# Speedup vs thread count
for r in rows:
    n = r["n"]
    speedups = [float(r[f"speedup_{t}t"]) for t in thread_counts]
    axes[0].plot(thread_counts, speedups, "o-", label=f"n={n}")
axes[0].axhline(1.0, color="black", linestyle="--", linewidth=1, label="Break-even (1.0x)")
axes[0].set_title("Speedup vs thread count (CPU-bound Python threading)")
axes[0].set_xlabel("Number of threads")
axes[0].set_ylabel("Speedup (sequential_time / parallel_time)")
axes[0].set_xticks(thread_counts)
axes[0].legend()
axes[0].grid(alpha=0.3)

# Absolute time vs thread count
for r in rows:
    n = r["n"]
    times = [float(r[f"parallel_{t}t_time"]) for t in thread_counts]
    axes[1].plot(thread_counts, times, "o-", label=f"n={n} (parallel)")
    axes[1].axhline(float(r["sequential_time"]), linestyle=":", alpha=0.6)
axes[1].set_title("Absolute runtime vs thread count\n(dotted lines = pure sequential baseline)")
axes[1].set_xlabel("Number of threads")
axes[1].set_ylabel("Time (seconds)")
axes[1].set_xticks(thread_counts)
axes[1].legend()
axes[1].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("task5_scalability.png", dpi=150)
print("Saved task5_scalability.png")
