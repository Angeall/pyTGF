import unittest
from characters.moves.continous import ContinuousMove
from characters.moves.move import ShortMove
from characters.units.moving_unit import MovingUnit
from display.tile import Tile


class Touchable:
    def __init__(self):
        self.touched = False
        self.touchCount = 0

    def touch(self):
        self.touched = True
        self.touchCount += 1


class TestContinuousMove(unittest.TestCase):
    def test_perform_step(self):
        """
        Makes sure each step is working correctly
        """
        unit = MovingUnit(speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        unit_tile = source_tile
        next_tile = destination_tile
        path = ContinuousMove(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60)
        for _ in range(59):
            path.performNextMove()
        unit_tile = destination_tile
        next_tile = source_tile
        path.performNextMove()
        self.assertEqual(path._currentMove.destinationTile, source_tile)

    def test_cancel(self):
        """
        Makes sure the cancel method is working correctly
        """
        unit = MovingUnit(speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        unit_tile = source_tile
        next_tile = destination_tile
        path = ContinuousMove(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60)
        for _ in range(59):
            path.performNextMove()
        path.cancel()
        path.performNextMove()
        self.assertTrue(path.cancelled)

    def test_actions(self):
        """
        Makes sure the actions are done right on time
        """
        unit = MovingUnit(speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        destination_tile.addNeighbour(source_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        pre_action_touchable = Touchable()
        post_action_touchable = Touchable()
        pre_step_action_touchable = Touchable()
        post_step_action_touchable = Touchable()
        unit_tile = source_tile
        next_tile = destination_tile
        path = ContinuousMove(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60,
                              pre_action=lambda: pre_action_touchable.touch(),
                              post_action=lambda: post_action_touchable.touch(),
                              step_pre_action=lambda: pre_step_action_touchable.touch(),
                              step_post_action=lambda: post_step_action_touchable.touch())
        path.performNextMove()
        self.assertTrue(pre_action_touchable.touched)
        self.assertEqual(pre_step_action_touchable.touchCount, 1)
        for _ in range(58):
            path.performNextMove()
        unit_tile = destination_tile
        next_tile = source_tile
        path.performNextMove()
        self.assertEqual(post_step_action_touchable.touchCount, 1)
        path.performNextMove()
        self.assertEqual(pre_action_touchable.touchCount, 1)  # The action must not be performed twice
        self.assertEqual(pre_step_action_touchable.touchCount, 2)
        for _ in range(58):
            path.performNextMove()
        unit_tile = source_tile
        next_tile = destination_tile
        path.performNextMove()
        self.assertEqual(post_step_action_touchable.touchCount, 2)
        self.assertEqual(post_action_touchable.touchCount, 0)
