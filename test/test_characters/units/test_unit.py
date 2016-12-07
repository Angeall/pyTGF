from characters.units.unit import Unit
from characters.particle import Particle
import unittest


class TestUnit(unittest.TestCase):
    def test_kill(self):
        """
        Tests if a unit is properly killed
        """
        unit = Unit()
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertFalse(unit.isAlive())

    def test_kill_multiple_lives(self):
        """
        Tests if a unit is properly killed
        """
        unit = Unit(nb_lives=2)
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertTrue(unit.isAlive())
        unit.kill()
        self.assertFalse(unit.isAlive())

    def test_has_particle(self):
        """
        Tests if a unit contains particle that are added to it
        """
        unit = Unit()
        particle1 = Particle()
        particle2 = Particle()
        unit.addParticle(particle1)
        self.assertTrue(unit.hasParticle(particle1))
        unit.addParticle(particle2)
        self.assertTrue(unit.hasParticle(particle2))
        unit.removeOldestParticle()
        self.assertFalse(unit.hasParticle(particle1))
        unit.removeParticle(particle2)
        self.assertFalse(unit.hasParticle(particle2))



