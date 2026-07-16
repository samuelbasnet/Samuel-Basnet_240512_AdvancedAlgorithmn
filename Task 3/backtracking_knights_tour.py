"""
Task 3 - Backtracking: Knight's Tour.

Find a sequence of knight moves visiting every square of an n x n board
exactly once.

Pure backtracking (no pruning) explores up to 8 branches per square,
giving a worst-case search space of O(8^(n^2)) - infeasible beyond very
small boards (n <= 5 in reasonable time without pruning).

Pruning strategies implemented:
  1. Bounds/visited check - only recurse into squares on the board that
     have not yet been visited (standard constraint propagation, prunes
     invalid branches immediately rather than exploring them).
  2. Warnsdorff's rule - at each step, greedily try the neighbouring
     square with the FEWEST onward moves first. This is a heuristic
     ordering (not a guarantee), but empirically it finds a full tour
     almost immediately for boards up to very large n, because it steers
     the search away from squares that would otherwise become
     unreachable "islands" later - i.e. it prunes the search space by
     avoiding dead ends early rather than discovering them deep in the
     recursion.
"""

from typing import List, Optional, Tuple

MOVES = [(2, 1), (1, 2), (-1, 2), (-2, 1),
         (-2, -1), (-1, -2), (1, -2), (2, -1)]


def _on_board(x, y, n):
    return 0 <= x < n and 0 <= y < n


def _degree(x, y, n, board):
    """Number of onward moves available from (x, y) - used by Warnsdorff's rule."""
    count = 0
    for dx, dy in MOVES:
        nx, ny = x + dx, y + dy
        if _on_board(nx, ny, n) and board[nx][ny] == -1:
            count += 1
    return count


def knights_tour(n: int, start: Tuple[int, int] = (0, 0), use_warnsdorff: bool = True):
    """Returns (success, board) where board[i][j] = move-order index (0-based),
    or -1 if that square was never reached (only possible if success is False).
    """
    board = [[-1] * n for _ in range(n)]
    sx, sy = start
    board[sx][sy] = 0
    nodes_explored = [0]

    def solve(x, y, move_count):
        nodes_explored[0] += 1
        if move_count == n * n:
            return True

        candidates = []
        for dx, dy in MOVES:
            nx, ny = x + dx, y + dy
            if _on_board(nx, ny, n) and board[nx][ny] == -1:
                candidates.append((nx, ny))

        if use_warnsdorff:
            # Pruning: try the neighbour with fewest onward options first
            candidates.sort(key=lambda c: _degree(c[0], c[1], n, board))

        for nx, ny in candidates:
            board[nx][ny] = move_count
            if solve(nx, ny, move_count + 1):
                return True
            board[nx][ny] = -1  # backtrack

        return False

    success = solve(sx, sy, 1)
    return success, board, nodes_explored[0]


def print_board(board):
    n = len(board)
    width = len(str(n * n))
    for row in board:
        print(" ".join(str(v).rjust(width) for v in row))
