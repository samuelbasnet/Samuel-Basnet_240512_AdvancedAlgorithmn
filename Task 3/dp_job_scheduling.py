"""
Task 3 - Dynamic Programming: Weighted Job Scheduling with Time Windows.

Given jobs each with (start, end, profit), select a subset of non-overlapping
jobs that maximises total profit.

Subproblem definition:
    Sort jobs by end time. Let dp[i] = maximum profit achievable using
    jobs[0..i-1] (the first i jobs in end-time order).

Recurrence:
    dp[0] = 0
    dp[i] = max( dp[i-1],                      # skip job i-1
                 profit[i-1] + dp[p(i-1)] )     # take job i-1
    where p(i-1) = number of jobs (in the sorted order) that end at or
    before start[i-1] (found via binary search, since jobs are sorted by end).

This is bottom-up tabulation: dp is filled left to right, each entry using
only previously computed entries, giving O(n log n) with binary search
(O(n) states x O(log n) per binary search lookup for p()), versus O(n^2)
with a naive linear scan for p(). We use the memo array as a table (not a
recursive memoised function) because the subproblems form a natural chain,
so bottom-up avoids recursion-depth/call overhead entirely.
"""

from bisect import bisect_right
from dataclasses import dataclass
from typing import List


@dataclass
class Job:
    start: int
    end: int
    profit: int
    name: str = ""


def weighted_job_scheduling(jobs: List[Job]):
    if not jobs:
        return 0, []

    jobs_sorted = sorted(jobs, key=lambda j: j.end)
    n = len(jobs_sorted)
    ends = [j.end for j in jobs_sorted]

    dp = [0] * (n + 1)          # dp[i] = best profit using first i sorted jobs
    take = [False] * (n + 1)    # whether job i-1 was taken in the optimal solution

    for i in range(1, n + 1):
        job = jobs_sorted[i - 1]
        # p = index (1-based) of the last job that ends <= job.start
        p = bisect_right(ends, job.start, 0, i - 1)  # search within jobs[0..i-2]
        include_profit = job.profit + dp[p]
        exclude_profit = dp[i - 1]
        if include_profit > exclude_profit:
            dp[i] = include_profit
            take[i] = True
        else:
            dp[i] = exclude_profit
            take[i] = False

    # Reconstruct the chosen jobs by walking back through the table
    chosen = []
    i = n
    while i > 0:
        if take[i]:
            job = jobs_sorted[i - 1]
            chosen.append(job)
            i = bisect_right(ends, job.start, 0, i - 1)
        else:
            i -= 1
    chosen.reverse()

    return dp[n], chosen


def brute_force_job_scheduling(jobs: List[Job]):
    """Exponential O(2^n) brute force for verification on small inputs."""
    best = [0, []]

    def overlaps(a, b):
        return a.start < b.end and b.start < a.end

    n = len(jobs)

    def rec(i, chosen, profit):
        if i == n:
            if profit > best[0]:
                best[0] = profit
                best[1] = list(chosen)
            return
        # skip
        rec(i + 1, chosen, profit)
        # take, if no conflict
        if all(not overlaps(jobs[i], c) for c in chosen):
            chosen.append(jobs[i])
            rec(i + 1, chosen, profit + jobs[i].profit)
            chosen.pop()

    rec(0, [], 0)
    return best[0], best[1]
