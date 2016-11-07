import unittest

import pygame

from display.boards.square_board import SquareBoardBuilder


class TestSquareBoard(unittest.TestCase):
    def test_numbers_of_tile(self):
        board = SquareBoardBuilder(pygame.Surface((10, 10)), 7, 6).create()
        self.assertEqual(len(board.tiles), 7)
        for line in board.tiles:
            self.assertEqual(len(line), 6)

    def test_tiles_position(self):
        width = 100
        height = 50
        x_margin = 20
        y_margin = 10
        nb_lines = 2
        nb_column = 5
        builder = SquareBoardBuilder(pygame.Surface((width, height)), nb_lines, nb_column)
        builder.setMargins(x_margin, y_margin)
        board = builder.create()
        center = board.tiles[0][0].center
        square_border_length = min((width - 2 * x_margin) / nb_column, (height - 2 * y_margin) / nb_lines)
        self.assertAlmostEqual(center[0],
                               ((width - square_border_length * nb_column) / 2) + square_border_length / 2,
                               delta=0.01)
        self.assertAlmostEqual(center[1],
                               ((height - square_border_length * nb_lines) / 2) + square_border_length / 2,
                               delta=0.01)
        center = board.tiles[1][2].center
        self.assertAlmostEqual(center[0],
                               ((width - square_border_length * nb_column) / 2) + square_border_length * 2.5,
                               delta=0.01)
        self.assertAlmostEqual(center[1],
                               ((height - square_border_length * nb_lines) / 2) + square_border_length * 1.5,
                               delta=0.01)

    def test_tile_neighbours(self):
        board = SquareBoardBuilder(pygame.Surface((10, 10)), 7, 6).create()
        self.assertTrue(board.getTileById((0, 0)).hasDirectAccess((0, 1)))
        self.assertTrue(board.getTileById((0, 3)).hasDirectAccess((1, 3)))
        self.assertTrue(board.getTileById((1, 3)).hasDirectAccess((0, 3)))
        self.assertTrue(board.getTileById((0, 2)).hasDirectAccess((0, 1)))

    def test_tile_nb_neighbours_on_borders(self):
        board = SquareBoardBuilder(pygame.Surface((10, 10)), 7, 6).create()
        self.assertTrue(len(board.getTileById((0, 0)).neighbours), 2)
        self.assertTrue(len(board.getTileById((6, 0)).neighbours), 2)
        self.assertTrue(len(board.getTileById((0, 5)).neighbours), 2)
        self.assertTrue(len(board.getTileById((6, 5)).neighbours), 2)

    def test_tile_nb_neighbours_on_sidelines(self):
        board = SquareBoardBuilder(pygame.Surface((10, 10)), 7, 6).create()
        self.assertTrue(len(board.getTileById((0, 2)).neighbours), 3)
        self.assertTrue(len(board.getTileById((6, 1)).neighbours), 3)
        self.assertTrue(len(board.getTileById((1, 5)).neighbours), 3)
        self.assertTrue(len(board.getTileById((2, 0)).neighbours), 3)

