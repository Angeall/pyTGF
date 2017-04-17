import unittest

from pytgf.board import Tile
from pytgf.characters.moves import ContinuousPath
from pytgf.characters.units import Unit


class Touchable:
    def __init__(self):
        self.touched = False
        self.touchCount = 0

    def touch(self):
        self.touched = True
        self.touchCount += 1


class TestContinuousPath(unittest.TestCase):
    def test_perform_step(self):
        """
        Makes sure each step is working correctly
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        unit_tile = source_tile
        next_tile = destination_tile
        unit_loc = {unit: source_tile.identifier}
        path = ContinuousPath(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60, units_location_dict=unit_loc)
        just_started, _, _ = path.performNextMove()
        self.assertTrue(just_started)
        for _ in range(58):
            path.performNextMove()
        unit_tile = destination_tile
        next_tile = source_tile
        just_started, move_completed, new_tile_id = path.performNextMove()
        self.assertTrue(move_completed)
        self.assertEqual(new_tile_id, destination_tile.identifier)

    def test_complete(self):
        """
        Makes sure the "complete" function is working correctly
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0), (0, 2)), walkable=True,
                                deadly=False)
        third_tile = Tile(identifier=(0, 2), center=(75, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        unit_loc = {unit: source_tile.identifier}
        my_tiles = [third_tile, destination_tile]
        # Distance separating the two tiles is 30 pixels
        unit_tiles = [destination_tile, source_tile]
        path = ContinuousPath(unit, lambda x: unit_tiles.pop(), lambda tile: my_tiles.pop(), fps=60, max_moves=1,
                              units_location_dict=unit_loc)
        new_tile_id = path.complete()
        self.assertFalse(new_tile_id == source_tile.identifier)
        self.assertTrue(new_tile_id == destination_tile.identifier)
        self.assertTrue(unit_loc[unit] is destination_tile.identifier)

    def test_stop(self):
        """
        Makes sure the stop method is working correctly
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        unit_loc = {unit: source_tile.identifier}
        # Distance separating the two tiles is 30 pixels
        unit_tile = source_tile
        next_tile = destination_tile
        path = ContinuousPath(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60, units_location_dict=unit_loc)
        for _ in range(59):
            path.performNextMove()
        path.stop()
        path.performNextMove()
        self.assertTrue(path.finished())

    def test_actions(self):
        """
        Makes sure the actions are done right on time
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        unit_loc = {unit: source_tile.identifier}
        # Distance separating the two tiles is 30 pixels
        pre_action_touchable = Touchable()
        post_action_touchable = Touchable()
        pre_step_action_touchable = Touchable()
        post_step_action_touchable = Touchable()
        unit_tile = source_tile
        next_tile = destination_tile
        path = ContinuousPath(unit, lambda x: unit_tile, lambda tile: next_tile, fps=60,
                              pre_action=pre_action_touchable.touch,
                              post_action=post_action_touchable.touch,
                              step_pre_action=pre_step_action_touchable.touch,
                              step_post_action=post_step_action_touchable.touch,
                              units_location_dict=unit_loc)
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
