import time
import threading
from game_logic import is_safe, SIZE


# ================= SEQUENTIAL =================
def solve_sequential():
    solutions = []
    board = [-1] * SIZE

    def backtrack(row):
        if row == SIZE:
            solutions.append(board.copy())
            return

        for col in range(SIZE):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(row + 1)
                board[row] = -1

    start = time.time()
    backtrack(0)
    end = time.time()

    return solutions, end - start


# ================= THREADED =================
def solve_threaded():
    solutions = []
    lock = threading.Lock()

    def worker(start_col):
        board = [-1] * SIZE
        board[0] = start_col

        def backtrack(row):
            if row == SIZE:
                with lock:
                    solutions.append(board.copy())
                return

            for col in range(SIZE):
                if is_safe(board, row, col):
                    board[row] = col
                    backtrack(row + 1)
                    board[row] = -1

        backtrack(1)

    threads = []
    start = time.time()

    for col in range(SIZE):
        t = threading.Thread(target=worker, args=(col,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()

    return solutions, end - start


# ================= ONE SOLUTION (FOR HINT / RED BOARD) =================
def get_one_solution():
    board = [-1] * SIZE

    def backtrack(row):
        if row == SIZE:
            return board.copy()

        for col in range(SIZE):
            if is_safe(board, row, col):
                board[row] = col
                result = backtrack(row + 1)
                if result:
                    return result
                board[row] = -1

        return None

    return backtrack(0)