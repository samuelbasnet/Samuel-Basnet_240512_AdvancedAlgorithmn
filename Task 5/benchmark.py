"""
Task 5: Empirical scalability test of concurrent merge sort.

Sorts City records (reusing Task 1's dataset generator) by population,
comparing the pure-sequential implementation against the threaded version
at 1, 2, 4, and 8 threads. Reports wall-clock time and speedup, and is
designed to surface (not hide) the effect of Python's GIL on CPU-bound
threaded code - see task5_analysis.md for the discussion this data feeds.
"""

import time
import random
import csv
import sys

sys.path.insert(0, "../task1")
from concurrent_merge_sort import sequential_merge_sort, parallel_merge_sort

try:
    from data_structures import City
except ImportError:
    # Fallback definition if task1 folder isn't alongside this one
    from dataclasses import dataclass

    @dataclass
    class City:
        name: str
        lat: float
        lon: float
        population: int
        distance: float = 0.0


def make_cities(n, seed=1):
    random.seed(seed)
    cities = []
    for i in range(n):
        cities.append(City(
            name=f"C{i:07d}", lat=random.uniform(-90, 90), lon=random.uniform(-180, 180),
            population=random.randint(1000, 5_000_000), distance=random.uniform(0, 10000),
        ))
    random.shuffle(cities)
    return cities


def time_fn(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return time.perf_counter() - start, result


def run_benchmark(sizes=(5000, 20000, 50000), thread_counts=(1, 2, 4, 8), repeats=3):
    rows = []

    for n in sizes:
        seq_times = []
        for r in range(repeats):
            cities = make_cities(n, seed=r)
            t, result = time_fn(sequential_merge_sort, list(cities), key=lambda c: c.population)
            assert result == sorted(cities, key=lambda c: c.population)
            seq_times.append(t)
        seq_avg = sum(seq_times) / repeats

        row = {"n": n, "sequential_time": seq_avg}

        for threads in thread_counts:
            par_times = []
            for r in range(repeats):
                cities = make_cities(n, seed=r)
                t, (result, stats) = time_fn(
                    parallel_merge_sort, list(cities), lambda c: c.population, threads
                )
                assert result == sorted(cities, key=lambda c: c.population)
                par_times.append(t)
            par_avg = sum(par_times) / repeats
            speedup = seq_avg / par_avg if par_avg > 0 else 0
            row[f"parallel_{threads}t_time"] = par_avg
            row[f"speedup_{threads}t"] = speedup

        rows.append(row)
        print(f"n={n:>6}  sequential={seq_avg:.5f}s  " +
              "  ".join(f"{t}t={row[f'parallel_{t}t_time']:.5f}s(x{row[f'speedup_{t}t']:.2f})"
                        for t in thread_counts))

    with open("task5_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved task5_results.csv")
    return rows


if __name__ == "__main__":
    run_benchmark()
