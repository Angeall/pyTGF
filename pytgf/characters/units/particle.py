"""
File containing the definition of a Particle.
"""

from copy import deepcopy
from typing import Optional

import pygame

from .sprite import UnitSprite
from ...utils.geom import vectorize, Coordinates

__author__ = 'Anthony Rouneau'


class Particle:
    """
    A Particle is something than can be placed on a tile of the game. It can be killed, drawn and moved.
    """

    def __init__(self, sprite: Optional[UnitSprite]=None, nb_lives: int=1, id_number: int=-1, speed: int=150):
        """
        Instantiates a particle unit in the game

        Args:
            sprite: The sprite to draw on the board (can be None if the Particle must not be drawn)
            nb_lives: The number of lives this unit has before it dies
            id_number: The number representing the player that owns this particle
        """
        self._nbLives = nb_lives
        self.sprite = sprite  # type: UnitSprite
        self.playerNumber = id_number
        self.speed = speed
        self._isAlive = True
        self._drawable = None

    def isAlive(self) -> bool:
        """
        Returns: True if the particle is alive, False otherwise.
        """
        return self._isAlive

    def setNbLives(self, nb_lives: int) -> None:
        """
        Sets the given number of lives of the particle

        Args:
            nb_lives: The number of lives to set to the particle
        """
        self._nbLives = nb_lives
        if self._nbLives <= 0:
            self._isAlive = False
        else:
            self._isAlive = True

    def kill(self) -> None:
        """
        Remove a life from the particle
        """
        self._nbLives -= 1
        if self._nbLives <= 0:
            self._isAlive = False

    def oneUp(self) -> None:
        """
        Adds a life to the particle
        """
        self._nbLives += 1
        if self._nbLives > 0:
            self._isAlive = True

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the particle on the given surface

        Args:
            surface: The surface the particle will be drawn on
        """
        if self.sprite is not None and self.sprite.rect is not None and self.isAlive():
            if self._drawable is None:
                self._drawable = pygame.sprite.RenderPlain(self.sprite)
            self._drawable.draw(surface)

    def moveTo(self, destination: Coordinates) -> None:
        """
        Move the center of the unit to the position

        Args:
            destination: The pixel on which the unit will be drawn.
        """
        if self.sprite is not None and self.sprite.rect is not None:
            current_position = self.sprite.rect.center
            if current_position != destination:
                x, y = vectorize(current_position, destination)
                self.sprite.rect.move_ip(x, y)

    def move(self, destination_offset: Coordinates) -> None:
        """
        Translate the unit by the given offset.

        Args:
            destination_offset: The translation offset to perform
        """
        if self.sprite is not None and self.sprite.rect is not None:
            self.sprite.rect.move_ip(destination_offset[0], destination_offset[1])

    def getSpriteGroup(self) -> pygame.sprite.Group:
        """
        Returns: The group consisting in the unit sprite
        """
        return self._drawable

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "sprite" and k != "_drawable":
                value = deepcopy(v, memo)
            else:
                value = None
            setattr(result, k, value)
        return result
