"""
Task 3: Empirical benchmarking for the three algorithmic paradigms.

1. DP (Weighted Job Scheduling): compare O(n log n) DP vs O(2^n) brute force
   runtime growth, and verify correctness by cross-checking on random inputs.
2. Greedy (Minimum Platforms): verify correctness against brute force, and
   time the greedy sweep's scaling with n.
3. Backtracking (Knight's Tour): compare nodes explored / time WITH vs
   WITHOUT the Warnsdorff pruning heuristic, to show the exponential
   worst-case being tamed in practice.
"""

import time
import random
import csv

from dp_job_scheduling import Job, weighted_job_scheduling, brute_force_job_scheduling
from greedy_platforms import min_platforms, brute_force_min_platforms
from backtracking_knights_tour import knights_tour


def time_fn(fn, *args):
    start = time.perf_counter()
    result = fn(*args)
    return time.perf_counter() - start, result


# ---------------------------------------------------------------------------
# 1. DP vs brute force
# ---------------------------------------------------------------------------
def bench_dp():
    print("=== DP: Weighted Job Scheduling (DP vs brute force) ===")
    rows = []
    random.seed(7)
    for n in [5, 10, 15, 18, 20, 22]:
        jobs = []
        for i in range(n):
            s = random.randint(0, 50)
            e = s + random.randint(1, 15)
            p = random.randint(1, 50)
            jobs.append(Job(s, e, p, str(i)))

        t_dp, (dp_profit, _) = time_fn(weighted_job_scheduling, jobs)

        if n <= 20:  # brute force becomes too slow beyond ~20
            t_bf, (bf_profit, _) = time_fn(brute_force_job_scheduling, jobs)
            assert dp_profit == bf_profit, f"Mismatch at n={n}: dp={dp_profit} bf={bf_profit}"
        else:
            t_bf = None

        row = {"n": n, "dp_time": t_dp, "brute_force_time": t_bf}
        rows.append(row)
        bf_str = f"{t_bf:.6f}s" if t_bf is not None else "skipped (too slow)"
        print(f"n={n:>3}  DP={t_dp:.6f}s  Brute-force={bf_str}")

    with open("task3_dp_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n", "dp_time", "brute_force_time"])
        writer.writeheader()
        writer.writerows(rows)
    print("Saved task3_dp_results.csv\n")
    return rows


# ---------------------------------------------------------------------------
# 2. Greedy: Minimum Platforms scaling + correctness
# ---------------------------------------------------------------------------
def bench_greedy():
    print("=== Greedy: Minimum Number of Platforms ===")
    rows = []
    random.seed(11)
    for n in [10, 50, 100, 500, 1000, 5000]:
        schedule = []
        for _ in range(n):
            a = random.randint(0, n * 2)
            d = a + random.randint(1, 30)
            schedule.append((a, d))

        t_greedy, (greedy_result, _) = time_fn(min_platforms, schedule)

        if n <= 500:  # brute force is O(n * distinct times), fine up to here
            t_bf, bf_result = time_fn(brute_force_min_platforms, schedule)
            assert greedy_result == bf_result, f"Mismatch n={n}: greedy={greedy_result} bf={bf_result}"
        else:
            t_bf = None

        row = {"n": n, "greedy_time": t_greedy, "brute_force_time": t_bf, "platforms": greedy_result}
        rows.append(row)
        bf_str = f"{t_bf:.6f}s" if t_bf is not None else "skipped (too slow)"
        print(f"n={n:>5}  Greedy={t_greedy:.6f}s  Brute-force={bf_str}  platforms_needed={greedy_result}")

    with open("task3_greedy_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["n", "greedy_time", "brute_force_time", "platforms"])
        writer.writeheader()
        writer.writerows(rows)
    print("Saved task3_greedy_results.csv\n")
    return rows


# ---------------------------------------------------------------------------
# 3. Backtracking: Knight's Tour, pruning vs no pruning
# ---------------------------------------------------------------------------
def bench_backtracking():
    print("=== Backtracking: Knight's Tour (pruning vs no pruning) ===")
    rows = []
    for n in [5, 6, 7, 8, 10, 12, 20]:
        t_pruned, (success_p, _, nodes_p) = time_fn(knights_tour, n, (0, 0), True)
        row = {"n": n, "warnsdorff_time": t_pruned, "warnsdorff_nodes": nodes_p, "warnsdorff_success": success_p}

        if n <= 6:  # unpruned backtracking explodes fast; cap it here
            t_unpruned, (success_u, _, nodes_u) = time_fn(knights_tour, n, (0, 0), False)
            row["no_pruning_time"] = t_unpruned
            row["no_pruning_nodes"] = nodes_u
            row["no_pruning_success"] = success_u
        else:
            row["no_pruning_time"] = None
            row["no_pruning_nodes"] = None
            row["no_pruning_success"] = None

        rows.append(row)
        np_str = (f"nodes={row['no_pruning_nodes']} time={row['no_pruning_time']:.6f}s"
                  if row["no_pruning_time"] is not None else "skipped (too slow)")
        print(f"n={n:>3}  Warnsdorff: nodes={nodes_p:>8} time={t_pruned:.6f}s success={success_p}  |  "
              f"No pruning: {np_str}")

    with open("task3_backtracking_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("Saved task3_backtracking_results.csv\n")
    return rows


if __name__ == "__main__":
    bench_dp()
    bench_greedy()
    bench_backtracking()
