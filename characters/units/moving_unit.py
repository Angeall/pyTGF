from characters.sprite import UnitSprite
from characters.units.unit import Unit


class MovingUnit(Unit):
    def __init__(self, sprite: UnitSprite=None, max_particles: int=-1, speed: int=150):
        """
        Instantiates a moving unit in the game
        Args:
            sprite: The sprite to draw on the board
            max_particles: The maximum number of particles for this unit (-1 = infinite)
            speed: The speed, in pixels per seconds, of the unit when moving
        """
        super().__init__(sprite, max_particles)
        self.speed = speed
        self.currentAction = None
