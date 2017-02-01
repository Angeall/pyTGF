import unittest

from pytgf.board.parser import BoardParser, IncorrectShapeError


class ExampleParser(BoardParser):
    def characterToTileProperties(self, character: str):
        if character == "W":
            return False, False
        elif character == "x":
            return True, True
        else:
            return True, False


class TestParser(unittest.TestCase):
    def test_ok_board(self):
        txt = "WWWxxxWWW   WWW\n   WWW   xxx   "
        board = ExampleParser().parse(txt)
        self.assertEqual(len(board), 2)
        self.assertEqual(len(board[0]), 15)
        self.assertEqual(board[0][0], (False, False))
        self.assertEqual(board[1][10], (True, True))
        self.assertEqual(board[1][8], (True, False))

    def test_non_rectangular_board(self):
        txt = "WWWxxxWWW   WWW\n   \n   WWW   xxx   "
        self.assertRaises(IncorrectShapeError, ExampleParser().parse, txt)