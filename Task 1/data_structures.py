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
    distance: float = 0.0





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
            node.value = value
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
            self._size += 1
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
        if bf > 1:
            if self._balance_factor(node.left) < 0:
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if bf < -1:
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





class MinHeap:
    """Array-based binary min-heap keyed on City.distance."""

    def __init__(self):
        self._data: List[City] = []

    def _swap(self, i, j):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def push(self, city: City) -> None:
        self._data.append(city)
        self._sift_up(len(self._data) - 1)

    def _sift_up(self, i):
        while i > 0:
            parent = (i - 1) // 2
            if self._data[parent].distance <= self._data[i].distance:
                break
            self._swap(parent, i)
            i = parent

    def pop(self) -> Optional[City]:
        if not self._data:
            return None
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def _sift_down(self, i):
        n = len(self._data)
        while True:
            left, right = 2 * i + 1, 2 * i + 2
            smallest = i
            if left < n and self._data[left].distance < self._data[smallest].distance:
                smallest = left
            if right < n and self._data[right].distance < self._data[smallest].distance:
                smallest = right
            if smallest == i:
                break
            self._swap(i, smallest)
            i = smallest

    def peek(self) -> Optional[City]:
        return self._data[0] if self._data else None

    def size(self) -> int:
        return len(self._data)





class HashTable:
    """Separate-chaining hash table with dynamic resizing (load factor 0.75)."""

    def __init__(self, capacity: int = 16):
        self._capacity = capacity
        self._buckets: List[List[Any]] = [[] for _ in range(capacity)]
        self._size = 0

    def _hash(self, key: str) -> int:
        return hash(key) % self._capacity

    def _resize(self):
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for k, v in bucket:
                self.insert(k, v)

    def insert(self, key: str, value: City) -> None:
        if self._size / self._capacity >= 0.75:
            self._resize()
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    def search(self, key: str) -> Optional[City]:
        idx = self._hash(key)
        for k, v in self._buckets[idx]:
            if k == key:
                return v
        return None

    def delete(self, key: str) -> None:
        idx = self._hash(key)
        bucket = self._buckets[idx]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket.pop(i)
                self._size -= 1
                return

    def size(self) -> int:
        return self._size

    def max_chain_length(self) -> int:
        return max((len(b) for b in self._buckets), default=0)