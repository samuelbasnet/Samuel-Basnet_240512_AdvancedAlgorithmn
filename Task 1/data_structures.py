"""
Task 1: Advanced Data Structures for a Route Planning Application
Implements: BST, AVL Tree, Min-Heap (priority queue), Hash Table (chaining)
Each stores a "City" record: name (key), coordinates, population, distance.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Any


@dataclass
class City:
    name: str
    lat: float
    lon: float
    population: int
    distance: float = 0.0  # e.g. distance from origin, used as heap priority


# ---------------------------------------------------------------------------
# Binary Search Tree (unbalanced)
# ---------------------------------------------------------------------------
class BSTNode:
    __slots__ = ("key", "value", "left", "right")

    def __init__(self, key: str, value: City):
        self.key = key
        self.value = value
        self.left: Optional["BSTNode"] = None
        self.right: Optional["BSTNode"] = None


class BST:
    """Plain binary search tree keyed by city name. O(h) ops, h can be O(n)."""

    def __init__(self):
        self.root: Optional[BSTNode] = None
        self._size = 0

    def insert(self, key: str, value: City) -> None:
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            self._size += 1
            return BSTNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value  # overwrite
        return node

    def search(self, key: str) -> Optional[City]:
        node = self.root
        while node is not None:
            if key == node.key:
                return node.value
            node = node.left if key < node.key else node.right
        return None

    def delete(self, key: str) -> None:
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            self._size -= 1
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            succ = node.right
            while succ.left is not None:
                succ = succ.left
            node.key, node.value = succ.key, succ.value
            node.right = self._delete_min(node.right)
            self._size += 1  # correct double-decrement from recursive call
        return node

    def _delete_min(self, node):
        if node.left is None:
            return node.right
        node.left = self._delete_min(node.left)
        return node

    def height(self) -> int:
        def h(node):
            if node is None:
                return 0
            return 1 + max(h(node.left), h(node.right))
        return h(self.root)

    def size(self) -> int:
        return self._size


# ---------------------------------------------------------------------------
# AVL Tree (self-balancing BST)
# ---------------------------------------------------------------------------
class AVLNode:
    __slots__ = ("key", "value", "left", "right", "height")

    def __init__(self, key: str, value: City):
        self.key = key
        self.value = value
        self.left: Optional["AVLNode"] = None
        self.right: Optional["AVLNode"] = None
        self.height = 1


class AVLTree:
    """Self-balancing BST guaranteeing O(log n) insert/search/delete."""

    def __init__(self):
        self.root: Optional[AVLNode] = None
        self._size = 0

    @staticmethod
    def _h(node) -> int:
        return node.height if node else 0

    def _update(self, node: AVLNode) -> None:
        node.height = 1 + max(self._h(node.left), self._h(node.right))

    def _balance_factor(self, node: AVLNode) -> int:
        return self._h(node.left) - self._h(node.right)

    def _rotate_right(self, y: AVLNode) -> AVLNode:
        x = y.left
        t2 = x.right
        x.right = y
        y.left = t2
        self._update(y)
        self._update(x)
        return x

    def _rotate_left(self, x: AVLNode) -> AVLNode:
        y = x.right
        t2 = y.left
        y.left = x
        x.right = t2
        self._update(x)
        self._update(y)
        return y

    def _rebalance(self, node: AVLNode) -> AVLNode:
        self._update(node)
        bf = self._balance_factor(node)
        if bf > 1:  # left heavy
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if bf < -1:  # right heavy
            if self._balance_factor(node.right) > 0:
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key: str, value: City) -> None:
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            self._size += 1
            return AVLNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node
        return self._rebalance(node)

    def search(self, key: str) -> Optional[City]:
        node = self.root
        while node is not None:
            if key == node.key:
                return node.value
            node = node.left if key < node.key else node.right
        return None

    def delete(self, key: str) -> None:
        self.root = self._delete(self.root, key)

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            self._size -= 1
            if node.left is None:
                return node.right
            if node.right is None:
                return node.left
            succ = node.right
            while succ.left is not None:
                succ = succ.left
            node.key, node.value = succ.key, succ.value
            node.right = self._delete(node.right, succ.key)
            self._size += 1
            return self._rebalance(node)
        return self._rebalance(node)

    def height(self) -> int:
        return self._h(self.root)

    def size(self) -> int:
        return self._size

