import unittest

from ....board import Tile
from ....characters.moves import ShortMove, ImpossibleMove, IllegalMove, InconsistentMove
from ....characters.units import Unit


class TestShortMove(unittest.TestCase):
    def test_perform_step(self):
        """
        Test that the good number of steps is performed to complete a move
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        unit_loc = {unit: source_tile.identifier}
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location=unit_loc)
        self.assertFalse(move.isPerformed)
        for _ in range(59):
            move.performStep()
        self.assertFalse(move.isPerformed)
        move.performStep()
        self.assertTrue(move.isPerformed)
        self.assertEqual(unit_loc[unit], destination_tile.identifier)

    def test_impossible_move(self):
        """
        Test that an impossible move raises the good exception
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=False, deadly=False)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location={unit: source_tile.identifier})
        self.assertRaises(ImpossibleMove, move.performStep)

    def test_inconsistent_move(self):
        """
        Test that a unit not placed on the source tile can not be moved from it
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=((0, 1),), walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60,
                         units_location={unit: destination_tile.identifier})
        self.assertRaises(InconsistentMove, move.performStep)

    def test_illegal_step(self):
        """
        Test that a illegal move raises the good exception
        """
        unit = Unit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile(identifier=(0, 0), center=(15, 15), neighbours=None, walkable=True, deadly=False)
        destination_tile = Tile(identifier=(0, 1), center=(45, 15), neighbours=((0, 0),), walkable=True, deadly=False)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60, units_location={unit: source_tile.identifier})
        self.assertRaises(IllegalMove, move.performStep)
