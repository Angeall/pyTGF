"""
File containing the definition of a unit that is designed to be controlled by a player (bot or human)
"""

from typing import Optional

from pytgf.characters.units import Unit
from pytgf.characters.units.sprite import UnitSprite


__author__ = 'Anthony Rouneau'


class MovingUnit(Unit):
    """
    Defines a unit that is designed to be moved by a controller in the game.
    """
    def __init__(self, player_number: int, sprite: Optional[UnitSprite]=None, max_particles: int=-1, nb_lives: int=1,
                 speed: int=150, surviving_particles: bool=False):
        """
        Instantiates a moving unit in the game
        Args:
            player_number: The number of the player represented by this moving unit
            sprite: The sprite to draw on the board (can be None if the Particle must not be drawn)
            max_particles: The maximum number of particles for this unit (-1 = infinite)
            nb_lives: The number of lives this unit has before it dies
            speed: The speed, in pixels per seconds, of the unit when moving
            surviving_particles: If true, the particles of this unit won't die with this unit
        """
        super().__init__(sprite, max_particles, nb_lives=nb_lives, surviving_particles=surviving_particles)
        self.playerNumber = player_number
        self.speed = speed
        self.currentAction = None
