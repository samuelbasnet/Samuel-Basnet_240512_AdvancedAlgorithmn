# Task 1: Advanced Data Structures (25 marks)

Route-planning data structures with empirical performance comparison.

## Files

| File | Purpose |
|---|---|
| `data_structures.py` | Core implementations: `BST`, `AVLTree`, `MinHeap`, `HashTable`, and the `City` record they all store. |
| `benchmark.py` | Times insert/search/delete for each structure at n = 100, 1,000, 10,000 (averaged over 3 runs with random insertion order). Writes `task1_results.csv`. |
| `plot_results.py` | Reads `task1_results.csv` and produces the comparison graphs. Must be run after `benchmark.py`. |
| `task1_results.csv` | Raw timing results from the benchmark run. |
| `task1_comparison.png` | Insertion time, search time, and tree-height comparisons across n. |
| `task1_loglog.png` | Log-log plot of insertion time vs n, used to visually confirm growth rate matches Big-O predictions. |
| `task1_analysis.md` | Written analysis: theoretical complexity table, discussion of hidden constant factors, empirical results table, and justification of which structure suits which use case. |

## How to run

```bash
python3 benchmark.py       # runs the timing experiments, writes task1_results.csv
python3 plot_results.py    # generates task1_comparison.png and task1_loglog.png
```

Requires `matplotlib` (`pip install matplotlib`). No other dependencies beyond the Python standard library.

## What each structure is for

- **BST** — plain binary search tree, no balancing. Cheapest insert, but height (and therefore search/delete cost) can degrade if keys arrive in sorted order.
- **AVL Tree** — self-balancing BST via rotations. Guarantees O(log n) height at all times, at the cost of extra bookkeeping per insert.
- **Min-Heap** — array-based binary heap keyed on `City.distance`, used as a priority queue (e.g. "next nearest city to visit"). Not designed for arbitrary search.
- **Hash Table** — separate chaining with automatic resize at load factor 0.75, for O(1)-average fast city lookup by name.

## Key results (see `task1_analysis.md` for full discussion)

At n = 10,000:
- AVL height stays at 16 vs BST's 32 — confirms AVL keeps O(log n) height even though both started from the same random insertion order.
- AVL insert (0.0613s) is ~4x slower than BST insert (0.0143s) due to rotation/height-update overhead — a real example of Big-O hiding constant factors.
- Hash Table search (0.00027s) is fastest overall; AVL search (0.00064s) overtakes BST search (0.00083s) at this scale, showing the balanced-height payoff.

## Verification

Correctness of each structure was checked against expected behaviour (sorted-order search, height bounds, heap pop ordering, delete-then-search) before benchmarking — see the inline sanity checks used during development for reference if you want to reproduce them.
