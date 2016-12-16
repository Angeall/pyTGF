import unittest
from board.tile import Tile
from characters.units.unit import Unit


class TestTile(unittest.TestCase):
    def test_add_neighbour(self):
        """
        Tests if a neighbour can be added correctly to the tile
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        self.assertEqual(len(tile.neighbours), 0)
        tile2 = Tile((0, 1), [(0, 1), (0, 1), (0, 1)], (0, 1))
        tile.addNeighbour(tile2.identifier)
        self.assertEqual(len(tile.neighbours), 1)
        self.assertTrue(tile.hasDirectAccess(tile2.identifier))

    def test_add_neighbours(self):
        """
        Tests if neighbours can be added added correctly to the tile
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        self.assertEqual(len(tile.neighbours), 0)
        tile2 = Tile((0, 1), [(0, 1), (0, 1), (0, 1)], (0, 1))
        tile3 = Tile((0, 2), [(0, 2), (0, 2), (0, 2)], (0, 2))
        tile4 = Tile((0, 3), [(0, 3), (0, 3), (0, 3)], (0, 3))
        tile.addNeighbours([tile2.identifier, tile3.identifier, tile4.identifier])
        self.assertEqual(len(tile.neighbours), 3)
        self.assertTrue(tile.hasDirectAccess(tile2.identifier))
        self.assertTrue(tile.hasDirectAccess(tile3.identifier))
        self.assertTrue(tile.hasDirectAccess(tile4.identifier))

    def test_contains_point(self):
        """
        Tests that the tile contains points inside of it
        """
        tile = Tile((15, 15), [(0, 0), (30, 0), (30, 30), (0, 30)], (0, 0))
        self.assertTrue(tile.containsPoint((15, 15)))
        self.assertTrue(tile.containsPoint((29, 1)))
        self.assertFalse(tile.containsPoint((31, 1)))
        self.assertFalse(tile.containsPoint((1, 31)))

    def test_remove_occupant(self):
        """
        Tests if a tile can clear its occupants successfully
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        unit = Unit()
        tile.addOccupant(unit)
        self.assertEqual(len(tile.occupants), 1)
        tile.removeOccupant(unit)
        self.assertEqual(len(tile.occupants), 0)

    def test_contains(self):
        """
        Tests if the contains method works
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        unit = Unit()
        unit2 = Unit()
        tile.addOccupant(unit)
        self.assertTrue(unit in tile)
        self.assertFalse(unit2 in tile)

    def test_dead_units(self):
        """
        Checks if dead units are removed correctly from the tile
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        unit = Unit()
        unit2 = Unit()
        tile.addOccupant(unit)
        tile.addOccupant(unit2)
        self.assertTrue(unit in tile)
        self.assertTrue(unit2 in tile)
        unit2.kill()
        self.assertTrue(unit in tile)
        self.assertFalse(unit2 in tile)

    def test_has_two_or_more_occupants(self):
        """
        Checks if the method "hasTwoOrMoreOccupants" works correctly
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        unit = Unit()
        unit2 = Unit()
        unit3 = Unit()
        tile.addOccupant(unit)
        self.assertFalse(tile.hasTwoOrMoreOccupants())
        tile.addOccupant(unit2)
        self.assertTrue(tile.hasTwoOrMoreOccupants())
        tile.addOccupant(unit3)
        self.assertTrue(tile.hasTwoOrMoreOccupants())
        tile.removeOccupant([unit2, unit3])
        self.assertFalse(tile.hasTwoOrMoreOccupants())

    def test_clear_occupants(self):
        """
        Tests if a tile can clear its occupants successfully
        """
        tile = Tile((0, 0), [(0, 0), (0, 0), (0, 0)], (0, 0))
        tile.addOccupant(Unit())
        tile.addOccupant(Unit())
        tile.addOccupant(Unit())
        self.assertEqual(len(tile.occupants), 3)
        tile.clearOccupants()
        self.assertEqual(len(tile.occupants), 0)


