import unittest

from ...board import Builder
from ...board.pathfinder import get_shortest_path, get_shortest_paths, reconstruct_path


class TestPathfinder(unittest.TestCase):
    def setUp(self):
        self.get_neighbours = lambda tile: tile.neighbours
        self.walkable = lambda tile: tile.walkable
        self.board = Builder(10, 10, 4, 4).create()

    def test_get_shortest_path_no_wall(self):
        path = get_shortest_path((0, 0), (0, 3), self.board.getTileById, self.get_neighbours, self.walkable)
        self.assertEqual(len(path), 3)
        self.assertEqual(path, [(0, 1), (0, 2), (0, 3)])

    def test_get_shortest_path_no_wall2(self):
        path = get_shortest_path((1, 1), (1, 2), self.board.getTileById, self.get_neighbours, self.walkable)
        self.assertEqual(len(path), 1)
        self.assertEqual(path, [(1, 2)])

    def test_get_shortest_path_with_wall(self):
        self.board.setTileNonWalkable((0, 2))
        path = get_shortest_path((0, 0), (0, 3), self.board.getTileById, self.get_neighbours, self.walkable)
        self.assertEqual(len(path), 5)
        self.assertEqual(path, [(0, 1), (1, 1), (1, 2), (1, 3), (0, 3)])

    def test_get_shortest_path_with_wall_deadly_prohibited(self):
        self.board.setTileNonWalkable((0, 2))
        self.board.setTileDeadly((1, 2))
        path = get_shortest_path((0, 0), (0, 3), self.board.getTileById, self.get_neighbours,
                                 lambda tile: tile.walkable and not tile.deadly)
        self.assertEqual(len(path), 7)
        self.assertEqual(path, [(0, 1), (1, 1), (2, 1), (2, 2), (2, 3), (1, 3), (0, 3)])

    def test_get_shortest_paths_no_wall(self):
        dijkstra_result = get_shortest_paths((0, 0), -1, self.board.getTileById, self.get_neighbours, self.walkable)
        path = reconstruct_path(dijkstra_result[0], (0, 0), (0, 3))
        self.assertEqual(len(path), 3)
        self.assertEqual(path, [(0, 1), (0, 2), (0, 3)])
        path = reconstruct_path(dijkstra_result[0], (0, 0), (1, 3))
        self.assertEqual(len(path), 4)

    def test_get_shortest_paths_no_wall_max_dist(self):
        dijkstra_result = get_shortest_paths((0, 0), 2, self.board.getTileById, self.get_neighbours, self.walkable)
        path = reconstruct_path(dijkstra_result[0], (0, 0), (0, 2))
        self.assertEqual(len(path), 2)
        self.assertEqual(path, [(0, 1), (0, 2)])

        self.assertRaises(Exception, reconstruct_path, dijkstra_result[0], (0, 0), (0, 3))
        self.assertFalse((0, 3) in dijkstra_result[0].keys())

