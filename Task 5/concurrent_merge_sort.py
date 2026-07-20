"""
Task 5: Concurrent Programming.

Implements a concurrent (multi-threaded) version of merge sort, applied to
the City dataset from Task 1, using Python's `threading` module (the
standard-library equivalent of POSIX threads for this environment).

Design:
  - The array is split recursively in half. Down to a configurable
    thread-count budget, the left and right halves are sorted in PARALLEL
    on separate threads; below that budget (or below a small-array
    threshold) sorting happens sequentially in the current thread to avoid
    the overhead of spawning threads for trivially small sub-problems.
  - Each thread works on a disjoint slice of the data (no two threads ever
    read/write the same array elements), so no lock is needed to protect
    the sort itself - this is a form of synchronisation-by-design (shared
    mutable state is simply avoided) rather than by locking.
  - A CRITICAL SECTION is nevertheless demonstrated explicitly: every
    thread must record its contribution (which slice it sorted, how many
    comparisons it made) into one shared statistics dictionary, which IS
    genuinely shared mutable state accessed by multiple threads. This is
    protected with a threading.Lock (mutex) around the read-modify-write
    of the shared dict, which is the correct and necessary synchronisation
    strategy here regardless of the interpreter's specific scheduling
    behaviour (see README / analysis for discussion of why this matters
    even under CPython's GIL).
"""

import threading
from typing import List, Callable, Any


class MergeSortStats:
    """Shared statistics object mutated by multiple threads - the critical section."""

    def __init__(self):
        self.lock = threading.Lock()
        self.thread_contributions = {}  # thread_name -> number of elements sorted
        self.total_comparisons = 0
        self.threads_spawned = 0

    def record_contribution(self, thread_name: str, n_elements: int, comparisons: int):
        # CRITICAL SECTION: multiple threads may call this concurrently.
        with self.lock:
            self.thread_contributions[thread_name] = (
                self.thread_contributions.get(thread_name, 0) + n_elements
            )
            self.total_comparisons += comparisons

    def record_thread_spawned(self):
        with self.lock:
            self.threads_spawned += 1


def _merge(left: List[Any], right: List[Any], key: Callable) -> (List[Any], int):
    result = []
    i = j = 0
    comparisons = 0
    while i < len(left) and j < len(right):
        comparisons += 1
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result, comparisons


def _sequential_merge_sort(arr: List[Any], key: Callable, stats: MergeSortStats = None) -> (List[Any], int):
    if len(arr) <= 1:
        if stats is not None:
            stats.record_contribution(threading.current_thread().name, len(arr), 0)
        return arr, 0
    mid = len(arr) // 2
    left, c1 = _sequential_merge_sort(arr[:mid], key, stats)
    right, c2 = _sequential_merge_sort(arr[mid:], key, stats)
    merged, c3 = _merge(left, right, key)
    total_comparisons = c1 + c2 + c3
    if stats is not None:
        stats.record_contribution(threading.current_thread().name, len(arr), c3)
    return merged, total_comparisons


def parallel_merge_sort(arr: List[Any], key: Callable = lambda x: x,
                         max_threads: int = 4, stats: MergeSortStats = None,
                         _depth_budget: int = None) -> List[Any]:
    """
    Sorts `arr` using up to `max_threads` concurrent worker threads.
    `_depth_budget` (internal) tracks how many more times we're allowed to
    fork into two threads before falling back to sequential recursion -
    this caps total threads spawned at roughly max_threads.
    """
    if stats is None:
        stats = MergeSortStats()

    if _depth_budget is None:
        # e.g. max_threads=4 -> budget=2 (2^2=4 leaf branches get their own thread)
        import math
        _depth_budget = max(0, int(math.log2(max(1, max_threads))))

    SEQUENTIAL_THRESHOLD = 64  # below this size, sequential recursion is faster than thread overhead

    def sort_slice(sub_arr, depth_budget):
        if len(sub_arr) <= 1:
            stats.record_contribution(threading.current_thread().name, len(sub_arr), 0)
            return sub_arr
        if len(sub_arr) <= SEQUENTIAL_THRESHOLD or depth_budget <= 0:
            result, comparisons = _sequential_merge_sort(sub_arr, key, stats)
            return result

        mid = len(sub_arr) // 2
        left_part, right_part = sub_arr[:mid], sub_arr[mid:]

        left_result = [None]
        right_result = [None]

        def left_worker():
            stats.record_thread_spawned()
            left_result[0] = sort_slice(left_part, depth_budget - 1)

        def right_worker():
            stats.record_thread_spawned()
            right_result[0] = sort_slice(right_part, depth_budget - 1)

        t_left = threading.Thread(target=left_worker, name=f"sort-L-d{depth_budget}")
        t_right = threading.Thread(target=right_worker, name=f"sort-R-d{depth_budget}")

        t_left.start()
        t_right.start()
        t_left.join()
        t_right.join()

        merged, comparisons = _merge(left_result[0], right_result[0], key)
        stats.record_contribution(threading.current_thread().name, len(sub_arr), comparisons)
        return merged

    sorted_arr = sort_slice(arr, _depth_budget)
    return sorted_arr, stats


def sequential_merge_sort(arr: List[Any], key: Callable = lambda x: x) -> List[Any]:
    result, _ = _sequential_merge_sort(arr, key)
    return result
