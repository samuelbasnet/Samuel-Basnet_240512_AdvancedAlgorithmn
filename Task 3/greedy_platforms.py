"""
Task 3 - Greedy: Minimum Number of Platforms.

Given train arrival and departure times, find the minimum number of
platforms required so that no two trains needing the same platform
ever overlap.

Greedy choice: sort arrivals and departures independently. Sweep through
events in time order; every arrival needs a free platform (increment
count), every departure frees one (decrement count). The running
maximum of "platforms in use" is the answer.

Why the greedy choice is optimal:
  At any instant t, the number of platforms required is exactly the number
  of trains whose [arrival, departure] interval contains t (i.e. the
  "interval overlap count" at t). The true answer is the maximum overlap
  count over all t. Sorting + sweeping computes exactly this maximum by
  processing events in time order and tracking a running count - it is not
  a heuristic approximation, it computes the exact maximum overlap, so the
  greedy sweep is optimal by construction (it directly computes the
  quantity being asked for, rather than approximating it).
"""

from typing import List, Tuple


def min_platforms(schedule: List[Tuple[int, int]]):
    """schedule: list of (arrival, departure) times (departure > arrival).
    Returns (min_platforms_needed, timeline) where timeline records the
    platform count after each event, for analysis/visualisation.
    """
    if not schedule:
        return 0, []

    arrivals = sorted(a for a, d in schedule)
    departures = sorted(d for a, d in schedule)

    n = len(schedule)
    i = j = 0
    platforms_needed = 0
    max_platforms = 0
    timeline = []

    # Sweep: an arrival that occurs at the same time as a departure is
    # processed as needing a platform first (train arriving needs one
    # even if another leaves at the exact same instant in most real
    # timetables); we process departures only strictly before arrivals.
    while i < n and j < n:
        if arrivals[i] < departures[j]:
            platforms_needed += 1
            max_platforms = max(max_platforms, platforms_needed)
            timeline.append(("arrival", arrivals[i], platforms_needed))
            i += 1
        else:
            platforms_needed -= 1
            timeline.append(("departure", departures[j], platforms_needed))
            j += 1

    return max_platforms, timeline


def brute_force_min_platforms(schedule: List[Tuple[int, int]]):
    """O(n * T) verification: for every relevant time instant, count overlaps."""
    if not schedule:
        return 0
    times = set()
    for a, d in schedule:
        times.add(a)
    max_count = 0
    for t in times:
        count = sum(1 for a, d in schedule if a <= t < d)
        max_count = max(max_count, count)
    return max_count
