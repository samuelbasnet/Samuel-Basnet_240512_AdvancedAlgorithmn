import csv
import matplotlib.pyplot as plt

with open("task1_results.csv") as f:
    rows = list(csv.DictReader(f))

ns = [int(r["n"]) for r in rows]

fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

# Insertion
axes[0].plot(ns, [float(r["bst_insert"]) for r in rows], "o-", label="BST")
axes[0].plot(ns, [float(r["avl_insert"]) for r in rows], "s-", label="AVL")
axes[0].plot(ns, [float(r["hash_insert"]) for r in rows], "^-", label="Hash Table")
axes[0].set_title("Insertion time vs n")
axes[0].set_xlabel("n (number of cities)")
axes[0].set_ylabel("Time (seconds)")
axes[0].legend()
axes[0].grid(alpha=0.3)

# Search
axes[1].plot(ns, [float(r["bst_search"]) for r in rows], "o-", label="BST")
axes[1].plot(ns, [float(r["avl_search"]) for r in rows], "s-", label="AVL")
axes[1].plot(ns, [float(r["hash_search"]) for r in rows], "^-", label="Hash Table")
axes[1].set_title("Search time vs n (n/10 lookups)")
axes[1].set_xlabel("n (number of cities)")
axes[1].set_ylabel("Time (seconds)")
axes[1].legend()
axes[1].grid(alpha=0.3)

# Height comparison BST vs AVL vs theoretical log2(n)
import math
axes[2].plot(ns, [float(r["bst_height"]) for r in rows], "o-", label="BST height")
axes[2].plot(ns, [float(r["avl_height"]) for r in rows], "s-", label="AVL height")
axes[2].plot(ns, [math.log2(n) for n in ns], "k--", label="log2(n) reference")
axes[2].set_title("Tree height vs n")
axes[2].set_xlabel("n (number of cities)")
axes[2].set_ylabel("Height")
axes[2].legend()
axes[2].grid(alpha=0.3)

plt.tight_layout()
plt.savefig("task1_comparison.png", dpi=150)
print("Saved task1_comparison.png")

