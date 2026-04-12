import unittest
from game_logic import is_valid_solution

class TestQueens(unittest.TestCase):

    def test_valid(self):
        board = [0,4,7,5,2,6,1,3]
        self.assertTrue(is_valid_solution(board))

    def test_invalid(self):
        board = [0,1,2,3,4,5,6,7]
        self.assertFalse(is_valid_solution(board))

if __name__ == "__main__":
    unittest.main()