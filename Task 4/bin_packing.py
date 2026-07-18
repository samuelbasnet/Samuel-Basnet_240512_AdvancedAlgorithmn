"""
Task 4: NP-Hard Problem - Multi-dimensional Bin Packing.

Problem: items have multiple resource requirements (CPU, RAM, bandwidth).
Pack all items into the minimum number of bins, where a bin's total usage
in EVERY dimension must not exceed its capacity in that dimension.

Why this is NP-Hard:
  Standard 1-D bin packing is already NP-Hard (it reduces from PARTITION:
  deciding whether a multiset of numbers can be split into two subsets of
  equal sum is exactly asking whether the items fit into 2 bins of size
  sum/2 -  so a bin-packing solver would solve PARTITION, an NP-Complete
  problem, in the process). Multi-dimensional bin packing contains 1-D
  bin packing as the special case where only one resource dimension is
  used, so it is at least as hard as 1-D bin packing - it is NP-Hard, and
  the decision version ("can this be packed into k bins?") is NP-Complete.
  Adding dimensions only removes solutions (a valid multi-D packing must
  satisfy every dimension simultaneously), so it never becomes easier.

Two heuristics implemented:
  1. Greedy construction: First-Fit Decreasing (FFD) generalised to
     multiple dimensions - sort items by a norm of their resource vector
     (descending), then place each item into the first bin with enough
     remaining capacity in ALL dimensions, opening a new bin if none fits.
  2. Local search (2-opt-style swap): starting from the FFD solution,
     repeatedly try swapping pairs of items between different bins if the
     swap keeps both bins feasible and reduces the number of "wasted"
     bins is not directly improvable, so instead we use the swap to
     reduce the maximum bin utilisation variance, which in turn creates
     opportunities to merge underfull bins - accept a swap only if it
     does not break feasibility and is not worse.
  3. Simulated Annealing: a stochastic search over full assignments of
     items to bins, occasionally accepting worse solutions early on
     (controlled by a cooling temperature) to escape local optima that a
     pure hill-climb would get stuck in.
"""

import math
import random
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class Item:
    name: str
    demands: Tuple[float, ...]  # e.g. (cpu, ram, bandwidth)


@dataclass
class BinCapacity:
    capacity: Tuple[float, ...]


def fits(bin_usage: List[float], item: Item, capacity: Tuple[float, ...]) -> bool:
    return all(bin_usage[d] + item.demands[d] <= capacity[d] for d in range(len(capacity)))


# ---------------------------------------------------------------------------
# Naive baseline: Next-Fit (only ever checks the single most recently opened
# bin, opening a new one the moment an item doesn't fit). Included purely as
# a deliberately weaker starting point to demonstrate what local search /
# simulated annealing can recover, since First-Fit-Decreasing alone is
# already close to optimal on the random instances tested (see analysis).
# ---------------------------------------------------------------------------
def next_fit(items: List[Item], capacity: Tuple[float, ...]):
    bins_usage: List[List[float]] = []
    bins_items: List[List[Item]] = []

    for item in items:  # no sorting - items processed in arrival order
        if bins_usage and fits(bins_usage[-1], item, capacity):
            for d in range(len(capacity)):
                bins_usage[-1][d] += item.demands[d]
            bins_items[-1].append(item)
        else:
            bins_usage.append(list(item.demands))
            bins_items.append([item])

    return bins_items, bins_usage


# ---------------------------------------------------------------------------
# Heuristic 1: Greedy - First-Fit Decreasing generalised to multiple dims
# ---------------------------------------------------------------------------
def first_fit_decreasing(items: List[Item], capacity: Tuple[float, ...]):
    # Sort by Euclidean norm of demand vector, descending (largest items first)
    sorted_items = sorted(items, key=lambda it: -math.sqrt(sum(d * d for d in it.demands)))

    bins_usage: List[List[float]] = []
    bins_items: List[List[Item]] = []

    for item in sorted_items:
        placed = False
        for i in range(len(bins_usage)):
            if fits(bins_usage[i], item, capacity):
                for d in range(len(capacity)):
                    bins_usage[i][d] += item.demands[d]
                bins_items[i].append(item)
                placed = True
                break
        if not placed:
            bins_usage.append(list(item.demands))
            bins_items.append([item])

    return bins_items, bins_usage


# ---------------------------------------------------------------------------
# Heuristic 2: Local search - try swapping items between bins to reduce
# the number of bins by emptying one out entirely.
# ---------------------------------------------------------------------------
def local_search_improve(bins_items: List[List[Item]], capacity: Tuple[float, ...], max_iters=500):
    bins_items = [list(b) for b in bins_items]

    def usage_of(bin_items):
        u = [0.0] * len(capacity)
        for it in bin_items:
            for d in range(len(capacity)):
                u[d] += it.demands[d]
        return u

    def try_empty_smallest_bin():
        # Attempt to move every item out of the least-full bin into other bins
        usages = [usage_of(b) for b in bins_items]
        norms = [sum(u) for u in usages]
        if not norms:
            return False
        idx = min(range(len(norms)), key=lambda i: norms[i])
        victim_items = bins_items[idx]

        placements = {}
        temp_usage = [usage_of(b) for i, b in enumerate(bins_items) if i != idx]
        other_indices = [i for i in range(len(bins_items)) if i != idx]

        for item in victim_items:
            placed = False
            for k, oi in enumerate(other_indices):
                if fits(temp_usage[k], item, capacity):
                    temp_usage[k] = [temp_usage[k][d] + item.demands[d] for d in range(len(capacity))]
                    placements[item.name] = oi
                    placed = True
                    break
            if not placed:
                return False  # can't empty this bin, abandon

        # Commit: remove bin idx, add its items to their target bins
        for item in victim_items:
            target = placements[item.name]
            bins_items[target].append(item)
        del bins_items[idx]
        return True

    improved = True
    iters = 0
    while improved and iters < max_iters:
        improved = try_empty_smallest_bin()
        iters += 1

    return bins_items


# ---------------------------------------------------------------------------
# Heuristic 3: Simulated Annealing over item->bin assignment
# ---------------------------------------------------------------------------
def simulated_annealing(items: List[Item], capacity: Tuple[float, ...],
                         initial_bins_items: List[List[Item]],
                         iterations=2000, start_temp=10.0, cooling=0.995, seed=0):
    rng = random.Random(seed)

    # Represent state as assignment: item_name -> bin_index
    n_bins_upper = len(initial_bins_items) + 2  # allow a couple of extra empty bins as "slack"
    assignment = {}
    for bidx, bin_items in enumerate(initial_bins_items):
        for it in bin_items:
            assignment[it.name] = bidx
    item_by_name = {it.name: it for it in items}

    def usage_per_bin(assign):
        usage = [[0.0] * len(capacity) for _ in range(n_bins_upper)]
        for name, b in assign.items():
            it = item_by_name[name]
            for d in range(len(capacity)):
                usage[b][d] += it.demands[d]
        return usage

    def cost(assign):
        usage = usage_per_bin(assign)
        bins_used = sum(1 for u in usage if sum(u) > 1e-9)
        # Penalise capacity violations heavily so SA is steered back to feasibility
        violation = 0.0
        for u in usage:
            for d in range(len(capacity)):
                if u[d] > capacity[d]:
                    violation += (u[d] - capacity[d])
        return bins_used + violation * 1000, bins_used, violation

    current_cost, _, _ = cost(assignment)
    best_assignment = dict(assignment)
    best_cost = current_cost
    temp = start_temp

    names = list(assignment.keys())

    for _ in range(iterations):
        name = rng.choice(names)
        old_bin = assignment[name]
        new_bin = rng.randrange(n_bins_upper)
        if new_bin == old_bin:
            continue

        assignment[name] = new_bin
        new_cost, bins_used, violation = cost(assignment)

        delta = new_cost - current_cost
        if delta < 0 or rng.random() < math.exp(-delta / max(temp, 1e-6)):
            current_cost = new_cost
            if current_cost < best_cost and violation == 0:
                best_cost = current_cost
                best_assignment = dict(assignment)
        else:
            assignment[name] = old_bin  # reject move

        temp *= cooling

    # Rebuild bins_items from best_assignment, dropping empty bins
    bins_map = {}
    for name, b in best_assignment.items():
        bins_map.setdefault(b, []).append(item_by_name[name])
    result_bins = [v for v in bins_map.values() if v]

    return result_bins, best_cost


def evaluate_solution(bins_items, capacity):
    """Returns (n_bins, feasible, avg_utilisation)."""
    feasible = True
    total_util = 0.0
    for bin_items in bins_items:
        usage = [0.0] * len(capacity)
        for it in bin_items:
            for d in range(len(capacity)):
                usage[d] += it.demands[d]
        for d in range(len(capacity)):
            if usage[d] > capacity[d] + 1e-9:
                feasible = False
        util = sum(usage[d] / capacity[d] for d in range(len(capacity))) / len(capacity)
        total_util += util
    avg_util = total_util / len(bins_items) if bins_items else 0
    return len(bins_items), feasible, avg_util
