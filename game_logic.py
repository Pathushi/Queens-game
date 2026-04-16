SIZE = 16      # The board dimensions (16x16)
QUEEN_COUNT = 8    # The number of queens to be placed

def is_safe(board, row, col):
    """Checks if a queen can be placed at board[row][col]"""
    for i in range(row):
        # board[i] might be -1 if no queen was placed in that row
        if board[i] == -1: continue 
        if board[i] == col or abs(board[i] - col) == abs(i - row):
            return False
    return True

def is_valid_solution(board):
    """Validates that exactly 8 queens are placed and none threaten each other."""
    placed_queens = [ (r, c) for r, c in enumerate(board) if c != -1 ]
    
    if len(placed_queens) != QUEEN_COUNT:
        return False

    for i in range(len(placed_queens)):
        for j in range(i + 1, len(placed_queens)):
            r1, c1 = placed_queens[i]
            r2, c2 = placed_queens[j]
            # Check column and diagonals
            if c1 == c2 or abs(c1 - c2) == abs(r1 - r2):
                return False
    return True