from board.boards.square_board import SquareBoardBuilder
from board.pathfinder import get_shortest_path, get_shortest_paths, reconstruct_path

import unittest


class TestPathfinder(unittest.TestCase):
    def setUp(self):
        self.board = SquareBoardBuilder(10, 10, 4, 4).create()

    def test_get_shortest_path_no_wall(self):
        path = get_shortest_path(self.board, (0, 0), (0, 3), None)
        self.assertEqual(len(path), 3)
        self.assertEqual(path, [(0, 1), (0, 2), (0, 3)])

    def test_get_shortest_path_no_wall2(self):
        path = get_shortest_path(self.board, (1, 1), (1, 2), None)
        self.assertEqual(len(path), 1)
        self.assertEqual(path, [(1, 2)])

    def test_get_shortest_path_with_wall(self):
        self.board.getTileById((0, 2)).walkable = False
        path = get_shortest_path(self.board, (0, 0), (0, 3), None)
        self.assertEqual(len(path), 5)
        self.assertEqual(path, [(0, 1), (1, 1), (1, 2), (1, 3), (0, 3)])

    def test_get_shortest_path_with_wall_deadly_prohibited(self):
        self.board.getTileById((0, 2)).walkable = False
        self.board.getTileById((1, 2)).deadly = True
        path = get_shortest_path(self.board, (0, 0), (0, 3), lambda tile: not tile.deadly)
        self.assertEqual(len(path), 7)
        self.assertEqual(path, [(0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (0, 3)])

    def test_get_shortest_paths_no_wall(self):
        dijkstra_result = get_shortest_paths(self.board, (0, 0), -1, None)
        path = reconstruct_path(dijkstra_result[0], (0, 0), (0, 3))
        self.assertEqual(len(path), 3)
        self.assertEqual(path, [(0, 1), (0, 2), (0, 3)])
        path = reconstruct_path(dijkstra_result[0], (0, 0), (1, 3))
        self.assertEqual(len(path), 4)

    def test_get_shortest_paths_no_wall_max_dist(self):
        dijkstra_result = get_shortest_paths(self.board, (0, 0), 2, None)
        path = reconstruct_path(dijkstra_result[0], (0, 0), (0, 2))
        self.assertEqual(len(path), 2)
        self.assertEqual(path, [(0, 1), (0, 2)])

        self.assertRaises(Exception, reconstruct_path, dijkstra_result[0], (0, 0), (0, 3))
        self.assertFalse((0, 3) in dijkstra_result[0].keys())

