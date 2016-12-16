import unittest
from characters.units.moving_unit import MovingUnit
from characters.moves.move import ShortMove, ImpossibleMove, IllegalMove
from board.tile import Tile


class TestShortMove(unittest.TestCase):
    def test_perform_step(self):
        """
        Test that the good number of steps is performed to complete a move
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        source_tile.addNeighbour(destination_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        self.assertFalse(move.isPerformed)
        for _ in range(59):
            move.performStep()
        self.assertFalse(move.isPerformed)
        move.performStep()
        self.assertTrue(move.isPerformed)

    # def test_deadly_move(self):
    #     """
    #     Test that a deadly move raises the good exception
    #     """
    #     unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
    #     source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
    #     destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1), deadly=True)
    #     source_tile.addNeighbour(destination_tile.identifier)
    #     # Distance separating the two tiles is 30 pixels
    #     move = ShortMove(unit, source_tile, destination_tile, fps=60)
    #     self.assertRaises(DeadlyMove, move.performStep)

    def test_impossible_move(self):
        """
        Test that an impossible move raises the good exception
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1), walkable=False)
        source_tile.addNeighbour(destination_tile.identifier)
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        self.assertRaises(ImpossibleMove, move.performStep)

    def test_illegal_step(self):
        """
        Test that a illegal move raises the good exception
        """
        unit = MovingUnit(1, speed=30)  # Speed = 30 pixels per second
        source_tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        destination_tile = Tile((45, 15), [(30, 0), (60, 0), (60, 30), (30, 30)], (0, 1))
        # Distance separating the two tiles is 30 pixels
        move = ShortMove(unit, source_tile, destination_tile, fps=60)
        self.assertRaises(IllegalMove, move.performStep)