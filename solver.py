import time
import threading
from game_logic import is_safe, SIZE, QUEEN_COUNT

# Optimized Backtracking
def solve_logic(limit_solutions=None):
    solutions = []
    board = [-1] * SIZE
    count = 0

    def backtrack(row, queens_placed):
        nonlocal count
        # Goal: We found 8 queens
        if queens_placed == QUEEN_COUNT:
            count += 1
            if limit_solutions is not None and len(solutions) < limit_solutions:
                solutions.append(board.copy())
            return

        # If we run out of rows before placing 8 queens, stop
        if row == SIZE:
            return

        # Option 1: Place a queen in this row
        for col in range(SIZE):
            if is_safe(board, row, col):
                board[row] = col
                backtrack(row + 1, queens_placed + 1)
                board[row] = -1
                if limit_solutions and count >= limit_solutions: return

        # Option 2: Skip this row (important since we only need 8 queens on 16 rows)
        # Only skip if there are enough rows left to still place the remaining queens
        if (SIZE - (row + 1)) >= (QUEEN_COUNT - queens_placed):
            backtrack(row + 1, queens_placed)

    start_time = time.time()
    backtrack(0, 0)
    end_time = time.time()
    
    return count, end_time - start_time

# ================= SEQUENTIAL =================
def solve_sequential():
    # We set a cap of 10,000 solutions for the DB to prevent massive lag
    # But it will still count the "Maximum"
    return solve_logic(limit_solutions=1000)

# ================= THREADED =================
def solve_threaded():
    """
    To make threading actually faster in Python for this, 
    we split the first row's decisions.
    """
    total_count = 0
    lock = threading.Lock()
    start_time = time.time()

    def worker(start_col):
        nonlocal total_count
        local_board = [-1] * SIZE
        local_count = 0

        def backtrack_threaded(row, queens_placed):
            nonlocal local_count
            if queens_placed == QUEEN_COUNT:
                local_count += 1
                return
            if row == SIZE:
                return

            for col in range(SIZE):
                if is_safe(local_board, row, col):
                    local_board[row] = col
                    backtrack_threaded(row + 1, queens_placed + 1)
                    local_board[row] = -1

            if (SIZE - (row + 1)) >= (QUEEN_COUNT - queens_placed):
                backtrack_threaded(row + 1, queens_placed)

        # Start by placing first queen in the assigned column
        local_board[0] = start_col
        backtrack_threaded(1, 1)
        
        # Also handle the case where the first row is skipped
        # (Only first thread handles the 'skip row 0' branch to avoid duplicates)
        if start_col == 0:
             backtrack_threaded(1, 0)

        with lock:
            total_count += local_count

    threads = []
    # Create threads based on columns of the first row
    for i in range(SIZE):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return total_count, time.time() - start_time