import unittest

from pytgf.board import Builder


class TestBoard(unittest.TestCase):
    def test_numbers_of_tile(self):
        """
        Makes sure that the number of tiles created is right
        """
        board = Builder(10, 10, 7, 6).create()
        self.assertEqual(board.lines, 7)
        self.assertEqual(board.columns, 6)
        self.assertEqual(len(board._tiles), 7)
        for i in range(7):
            self.assertEqual(len(board._tiles[i]), 6)

    def test_board_borders(self):
        """
        Makes sure that the borders are well defined on the border
        """
        builder = Builder(100, 100, 6, 6)
        builder.setMargins(20, 20)
        board = builder.create()
        borders = board.graphics._borders
        self.assertEqual(len(borders), 4)
        self.assertEqual(len(borders[0]), 2)
        self.assertTrue(((20, 20), (80, 20)) in borders)
        self.assertTrue(((80, 20), (80, 80)) in borders)
        self.assertTrue(((80, 80), (20, 80)) in borders)
        self.assertTrue(((20, 80), (20, 20)) in borders)

    def test_tiles_position(self):
        """
        Assures that the created tiles are located on the right pixels
        """
        width = 100
        height = 50
        x_margin = 20
        y_margin = 10
        nb_lines = 2
        nb_column = 5
        builder = Builder(width, height, nb_lines, nb_column)
        builder.setMargins(x_margin, y_margin)
        board = builder.create()
        center = board.getTileById((0, 0)).center
        square_border_length = min((width - 2 * x_margin) / nb_column, (height - 2 * y_margin) / nb_lines)
        self.assertAlmostEqual(center[0],
                               ((width - square_border_length * nb_column) / 2) + square_border_length / 2,
                               delta=0.01)
        self.assertAlmostEqual(center[1],
                               ((height - square_border_length * nb_lines) / 2) + square_border_length / 2,
                               delta=0.01)
        center = board.getTileById((1, 2)).center
        self.assertAlmostEqual(center[0],
                               ((width - square_border_length * nb_column) / 2) + square_border_length * 2.5,
                               delta=0.01)
        self.assertAlmostEqual(center[1],
                               ((height - square_border_length * nb_lines) / 2) + square_border_length * 1.5,
                               delta=0.01)

    def test_tile_neighbours(self):
        """
        Assures that the neighbours of some tiles are well defined
        """
        board = Builder(10, 10, 7, 6).create()
        self.assertTrue(board.isAccessible((0, 0), (0, 1)))
        self.assertTrue(board.isAccessible((0, 3), (1, 3)))
        self.assertTrue(board.isAccessible((1, 3), (0, 3)))
        self.assertTrue(board.isAccessible((0, 2), (0, 1)))

    def test_tile_nb_neighbours_on_borders(self):
        """
        Assures that the neighbours of border tiles are well defined
        """
        board = Builder(10, 10, 7, 6).create()
        self.assertTrue(len(board.getNeighboursIdentifier((0, 0))), 2)
        self.assertTrue(len(board.getNeighboursIdentifier((6, 0))), 2)
        self.assertTrue(len(board.getNeighboursIdentifier((0, 5))), 2)
        self.assertTrue(len(board.getNeighboursIdentifier((6, 5))), 2)

    def test_tile_nb_neighbours_on_sidelines(self):
        """
        Assures that the neighbours of sidelines tiles are well defined
        """
        board = Builder(10, 10, 7, 6).create()
        self.assertTrue(len(board.getNeighboursIdentifier((0, 2))), 3)
        self.assertTrue(len(board.getNeighboursIdentifier((6, 1))), 3)
        self.assertTrue(len(board.getNeighboursIdentifier((1, 5))), 3)
        self.assertTrue(len(board.getNeighboursIdentifier((2, 0))), 3)

    def test_tile_set_walkable(self):
        board = Builder(10, 10, 7, 6).create()
        self.assertTrue(board.getTileById((5, 5)).walkable)
        board.setTileNonWalkable((5, 5), False)
        self.assertFalse(board.getTileById((5, 5)).walkable)
        board.setTileNonWalkable((5, 5), True)
        self.assertTrue(board.getTileById((5, 5)).walkable)

    def test_tile_set_deadly(self):
        board = Builder(10, 10, 7, 6).create()
        self.assertFalse(board.getTileById((5, 5)).deadly)
        board.setTileDeadly((5, 5), True)
        self.assertTrue(board.getTileById((5, 5)).deadly)
        board.setTileDeadly((5, 5), False)
        self.assertFalse(board.getTileById((5, 5)).deadly)

    def test_get_tile_by_pixel(self):
        builder = Builder(10, 10, 5, 5)
        builder.setMargins(0, 0)
        board = builder.create()
        tile = board.getTileByPixel((1, 1))
        self.assertEqual(tile, board.getTileById((0, 0)))
        tile = board.getTileByPixel((3, 5))
        self.assertEqual(tile, board.getTileById((2, 1)))
        tile = board.getTileByPixel((9, 7))
        self.assertEqual(tile, board.getTileById((3, 4)))




