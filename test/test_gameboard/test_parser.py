import unittest

from gameboard.boards.square_board import SquareBoardBuilder
from gameboard.parsers.board_parser import BoardParser, IncorrectShapeError
from gameboard.tile import Tile


class DeadlyTile(Tile):
    def __init__(self, center: tuple, points: list, identifier):
        super().__init__(center, points, identifier, deadly=True)


class NonWalkableTile(Tile):
    def __init__(self, center: tuple, points: list, identifier):
        super().__init__(center, points, identifier, walkable=False)


class ExampleParser(BoardParser):
    def characterToTileType(self, character: str):
        if character == "W":
            return NonWalkableTile
        elif character == "x":
            return DeadlyTile
        else:
            return Tile


class TestParser(unittest.TestCase):
    def test_ok_board(self):
        txt = "WWWxxxWWW   WWW\n   WWW   xxx   "
        board = ExampleParser().parse(txt)
        self.assertEqual(len(board), 2)
        self.assertEqual(len(board[0]), 15)
        self.assertEqual(board[0][0], NonWalkableTile)
        self.assertEqual(board[1][10], DeadlyTile)
        self.assertEqual(board[1][8], Tile)

    def test_non_rectangular_board(self):
        txt = "WWWxxxWWW   WWW\n   \n   WWW   xxx   "
        self.assertRaises(IncorrectShapeError, ExampleParser().parse, txt)