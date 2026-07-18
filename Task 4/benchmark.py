"""
Task 4: Empirical comparison of heuristics for Multi-dimensional Bin Packing.

Compares:
  - Next-Fit         (weak greedy baseline, included to give the other
                       heuristics something meaningful to improve on)
  - First-Fit Decreasing (main greedy construction heuristic)
  - Local search      (starts from Next-Fit, tries to empty out bins)
  - Simulated Annealing (starts from Next-Fit, stochastic search)

Reports bin count (solution quality - fewer bins is better) and runtime
for each, across several random instance sizes.
"""

import time
import random
import csv

from bin_packing import (
    Item, next_fit, first_fit_decreasing, local_search_improve,
    simulated_annealing, evaluate_solution,
)


def make_items(n, seed):
    random.seed(seed)
    return [Item(f"item{i}", tuple(random.uniform(5, 35) for _ in range(3))) for i in range(n)]


def time_fn(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - start, result


def run_benchmark(sizes=(20, 40, 60, 100), repeats=5, capacity=(100.0, 100.0, 100.0)):
    rows = []

    for n in sizes:
        nf_bins_list, ffd_bins_list, ls_bins_list, sa_bins_list = [], [], [], []
        nf_t = ffd_t = ls_t = sa_t = 0.0

        for r in range(repeats):
            items = make_items(n, seed=1000 + r)

            t, (nf_result, _) = time_fn(next_fit, items, capacity)
            n_nf, feas_nf, _ = evaluate_solution(nf_result, capacity)
            nf_t += t; nf_bins_list.append(n_nf)

            t, (ffd_result, _) = time_fn(first_fit_decreasing, items, capacity)
            n_ffd, feas_ffd, _ = evaluate_solution(ffd_result, capacity)
            ffd_t += t; ffd_bins_list.append(n_ffd)

            t, ls_result = time_fn(local_search_improve, nf_result, capacity)
            n_ls, feas_ls, _ = evaluate_solution(ls_result, capacity)
            ls_t += t; ls_bins_list.append(n_ls)

            t, (sa_result, _) = time_fn(
                simulated_annealing, items, capacity, nf_result, 6000, 10.0, 0.995, r
            )
            n_sa, feas_sa, _ = evaluate_solution(sa_result, capacity)
            sa_t += t; sa_bins_list.append(n_sa)

            assert feas_nf and feas_ffd and feas_ls and feas_sa, "Infeasible solution produced!"

        row = {
            "n_items": n,
            "next_fit_bins_avg": sum(nf_bins_list) / repeats,
            "ffd_bins_avg": sum(ffd_bins_list) / repeats,
            "local_search_bins_avg": sum(ls_bins_list) / repeats,
            "sa_bins_avg": sum(sa_bins_list) / repeats,
            "next_fit_time": nf_t / repeats,
            "ffd_time": ffd_t / repeats,
            "local_search_time": ls_t / repeats,
            "sa_time": sa_t / repeats,
        }
        rows.append(row)
        print(f"n={n:>4}  bins(avg): NextFit={row['next_fit_bins_avg']:.1f}  "
              f"FFD={row['ffd_bins_avg']:.1f}  LocalSearch={row['local_search_bins_avg']:.1f}  "
              f"SA={row['sa_bins_avg']:.1f}  |  time(s): NF={row['next_fit_time']:.5f} "
              f"FFD={row['ffd_time']:.5f} LS={row['local_search_time']:.5f} SA={row['sa_time']:.5f}")

    with open("task4_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved task4_results.csv")
    return rows


if __name__ == "__main__":
    run_benchmark()
