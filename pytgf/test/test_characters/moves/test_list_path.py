import unittest

from pytgf.board import Tile
from pytgf.characters.moves import ListPath, ShortMove
from pytgf.characters.units import MovingUnit


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
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        unit_loc = {unit: source_tile.identifier}
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location=unit_loc)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60, units_location=unit_loc)

        path = ListPath(unit, [move, move2])
        for _ in range(60):
            path.performNextMove()
        self.assertTrue(unit_loc[unit] is destination_tile.identifier)
        self.assertTrue(move._unitsLocation[unit] is destination_tile.identifier)
        self.assertTrue(move2._unitsLocation[unit] is destination_tile.identifier)
        self.assertFalse(path.completed)
        for _ in range(59):
            path.performNextMove()
        self.assertFalse(path.completed)
        path.performNextMove()
        self.assertTrue(path.completed)

    def test_complete(self):
        """
        Makes sure the "complete" is working correctly
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location={unit: source_tile.identifier})

        path = ListPath(unit, [move])
        path.complete()
        self.assertTrue(path.completed)

    def test_stop(self):
        """
        Makes sure the stop method is working correctly
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        unit_loc = {unit: source_tile.identifier}
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location=unit_loc)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60, units_location=unit_loc)

        path = ListPath(unit, [move, move2])
        for _ in range(59):
            path.performNextMove()
        path.stop()
        self.assertFalse(path.stopped)
        path.performNextMove()
        self.assertTrue(path.stopped)
        self.assertTrue(unit_loc[unit] is destination_tile.identifier)

    def test_actions(self):
        """
        Makes sure the actions are done right on time
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        unit_loc = {unit: source_tile.identifier}

        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location=unit_loc)
        move2 = ShortMove(unit, destination_tile, source_tile, fps=60, units_location=unit_loc)

        pre_action_touchable = Touchable()
        post_action_touchable = Touchable()
        pre_step_action_touchable = Touchable()
        post_step_action_touchable = Touchable()
        path = ListPath(unit, [move, move2],
                        pre_action=pre_action_touchable.touch,
                        post_action=post_action_touchable.touch,
                        step_pre_action=pre_step_action_touchable.touch,
                        step_post_action=post_step_action_touchable.touch)
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
