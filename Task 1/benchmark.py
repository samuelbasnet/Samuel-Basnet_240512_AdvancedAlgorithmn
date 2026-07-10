"""
Task 1: Empirical performance testing of BST, AVL, Hash Table, Min-Heap.
Measures wall-clock time for insertion, search, deletion at n = 100, 1000, 10000.
Produces a results table (CSV) and comparison plots.
"""

import time
import random
import csv
import sys
import gc
from data_structures import BST, AVLTree, MinHeap, HashTable, City

sys.setrecursionlimit(20000)  # BST/AVL recursion can get deep for n=10000


def make_cities(n, seed=42):
    random.seed(seed)
    cities = []
    for i in range(n):
        cities.append(City(
            name=f"C{i:07d}",
            lat=random.uniform(-90, 90),
            lon=random.uniform(-180, 180),
            population=random.randint(1000, 5_000_000),
            distance=random.uniform(0, 10000),
        ))
    random.shuffle(cities)  # random insertion order (worst case for BST is sorted order)
    return cities


def time_it(fn, *args):
    gc.disable()
    start = time.perf_counter()
    result = fn(*args)
    elapsed = time.perf_counter() - start
    gc.enable()
    return elapsed, result


def bench_tree(tree_cls, cities, search_keys, delete_keys):
    tree = tree_cls()

    t_insert, _ = time_it(lambda: [tree.insert(c.name, c) for c in cities])
    t_search, _ = time_it(lambda: [tree.search(k) for k in search_keys])
    t_delete, _ = time_it(lambda: [tree.delete(k) for k in delete_keys])

    return {
        "insert": t_insert,
        "search": t_search,
        "delete": t_delete,
        "height": tree.height(),
    }




def bench_heap(cities):
    heap = MinHeap()
    t_push, _ = time_it(lambda: [heap.push(c) for c in cities])
    n_pops = max(1, len(cities) // 10)  # pop 10% to time extract-min

    def do_pops():
        for _ in range(n_pops):
            heap.pop()

    t_pop, _ = time_it(do_pops)
    return {
        "push_total": t_push,
        "push_per_op": t_push / len(cities),
        "pop_total_for_10pct": t_pop,
        "pop_per_op": t_pop / n_pops,
    }


def run_all(sizes=(100, 1000, 10000), repeats=3):
    all_rows = []
    for n in sizes:
        insert_bst = insert_avl = insert_ht = 0.0
        search_bst = search_avl = search_ht = 0.0
        delete_bst = delete_avl = delete_ht = 0.0
        height_bst = height_avl = 0
        heap_push = heap_pop = 0.0

        for r in range(repeats):
            cities = make_cities(n, seed=100 + r)
            search_keys = [c.name for c in random.sample(cities, min(len(cities), max(1, n // 10)))]
            delete_keys = [c.name for c in random.sample(cities, min(len(cities), max(1, n // 10)))]

            res_bst = bench_tree(BST, cities, search_keys, delete_keys)
            res_avl = bench_tree(AVLTree, cities, search_keys, delete_keys)
            res_ht = bench_hashtable(cities, search_keys, delete_keys)
            res_heap = bench_heap(cities)

            insert_bst += res_bst["insert"]; search_bst += res_bst["search"]; delete_bst += res_bst["delete"]
            insert_avl += res_avl["insert"]; search_avl += res_avl["search"]; delete_avl += res_avl["delete"]
            insert_ht += res_ht["insert"]; search_ht += res_ht["search"]; delete_ht += res_ht["delete"]
            height_bst += res_bst["height"]; height_avl += res_avl["height"]
            heap_push += res_heap["push_total"]; heap_pop += res_heap["pop_per_op"]

        row = {
            "n": n,
            "bst_insert": insert_bst / repeats,
            "bst_search": search_bst / repeats,
            "bst_delete": delete_bst / repeats,
            "bst_height": height_bst / repeats,
            "avl_insert": insert_avl / repeats,
            "avl_search": search_avl / repeats,
            "avl_delete": delete_avl / repeats,
            "avl_height": height_avl / repeats,
            "hash_insert": insert_ht / repeats,
            "hash_search": search_ht / repeats,
            "hash_delete": delete_ht / repeats,
            "heap_push_total": heap_push / repeats,
            "heap_pop_per_op": heap_pop / repeats,
        }
        all_rows.append(row)
        print(f"n={n:>6}  BST(insert/search/delete)={row['bst_insert']:.5f}/{row['bst_search']:.5f}/{row['bst_delete']:.5f}s "
              f"height={row['bst_height']:.0f}  |  AVL={row['avl_insert']:.5f}/{row['avl_search']:.5f}/{row['avl_delete']:.5f}s "
              f"height={row['avl_height']:.0f}  |  Hash={row['hash_insert']:.5f}/{row['hash_search']:.5f}/{row['hash_delete']:.5f}s")
    return all_rows


if __name__ == "__main__":
    rows = run_all()
    with open("task1_results.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print("\nSaved results to task1_results.csv")
