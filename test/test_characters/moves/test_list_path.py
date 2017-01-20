import unittest
from characters.moves.listpath import ListPath
from characters.moves.move import ShortMove
from characters.units.moving_unit import MovingUnit
from board.tile import Tile


class Touchable:
    def __init__(self):
        self.touched = False
        self.touchCount = 0

    def touch(self):
        self.touched = True
        self.touchCount += 1


class TestListPath(unittest.TestCase):
    def test_perform_step(self):
        """
        Makes sure each step is working correctly
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        source_tile.addOccupant(unit)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60)

        path = ListPath([move, move2])
        for _ in range(119):
            path.performNextMove()
        self.assertFalse(path.completed)
        path.performNextMove()
        self.assertTrue(path.completed)
        self.assertTrue(unit in source_tile)

    def test_complete(self):
        """
        Makes sure the "complete" is working correctly
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        source_tile.addOccupant(unit)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)

        path = ListPath([move])
        path.complete()
        self.assertTrue(path.completed)
        self.assertTrue(unit in destination_tile)

    def test_cancel(self):
        """
        Makes sure the cancel method is working correctly
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        source_tile.addOccupant(unit)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60)

        path = ListPath([move, move2])
        for _ in range(59):
            path.performNextMove()
        path.stop()
        self.assertFalse(path.stopped)
        path.performNextMove()
        self.assertTrue(path.stopped)

    def test_actions(self):
        """
        Makes sure the actions are done right on time
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        source_tile.addOccupant(unit)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60)

        pre_action_touchable = Touchable()
        post_action_touchable = Touchable()
        pre_step_action_touchable = Touchable()
        post_step_action_touchable = Touchable()
        path = ListPath([move, move2],
                        pre_action=lambda: pre_action_touchable.touch(),
                        post_action=lambda: post_action_touchable.touch(),
                        step_pre_action=lambda: pre_step_action_touchable.touch(),
                        step_post_action=lambda: post_step_action_touchable.touch())
        path.performNextMove()
        self.assertTrue(pre_action_touchable.touched)
        self.assertEqual(pre_step_action_touchable.touchCount, 1)
        for _ in range(59):
            path.performNextMove()
        self.assertEqual(post_step_action_touchable.touchCount, 1)
        path.performNextMove()
        self.assertEqual(pre_action_touchable.touchCount, 1)  # The action must not be performed twice
        self.assertEqual(pre_step_action_touchable.touchCount, 2)
        for _ in range(59):
            path.performNextMove()
        self.assertEqual(post_step_action_touchable.touchCount, 2)
        self.assertEqual(post_action_touchable.touchCount, 1)
