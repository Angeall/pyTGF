import unittest

from ....characters.units import Entity, Unit


class TestUnit(unittest.TestCase):
    def test_kill(self):
        """
        Tests if a unit is properly killed
        """
        unit = Unit(1)
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertFalse(unit.isAlive())

    def test_kill_multiple_lives(self):
        """
        Tests if a unit is properly killed
        """
        unit = Unit(1, nb_lives=2)
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertFalse(unit.isAlive())

    def test_has_entity(self):
        """
        Tests if a unit contains entity that are added to it
        """
        unit = Unit(1)
        entity1 = Entity()
        entity2 = Entity()
        unit.addentity(entity1)
        self.assertTrue(unit.hasentity(entity1))
        unit.addentity(entity2)
        self.assertTrue(unit.hasentity(entity2))
        unit.removeOldestentity()
        self.assertFalse(unit.hasentity(entity1))
        unit.removeentity(entity2)
        self.assertFalse(unit.hasentity(entity2))



