import pygame

import utils.geom
from characters.sprite import UnitSprite


class Particle:
    def __init__(self, sprite: UnitSprite=None):
        """
        Instantiates a particle unit in the game
        Args:
            sprite: The sprite to draw on the board
        """
        self.sprite = sprite  # type: UnitSprite
        self._drawable = None
        self._isAlive = True

    def isAlive(self) -> bool:
        """
        Returns: True if the particle is alive, False otherwise.
        """
        return self._isAlive

    def kill(self) -> bool:
        """
        Kills the particle
        """
        self._isAlive = False

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the particle on the given surface
        Args:
            surface: The surface the particle will be drawn on
        """
        if self.sprite is not None and self.isAlive():
            if self._drawable is None:
                self._drawable = pygame.sprite.RenderPlain(self.sprite)
            self._drawable.draw(surface)

    def moveTo(self, destination: tuple) -> None:
        """
        Move the center of the unit to the position
        Args:
            destination: The pixel on which the unit will be drawn.
        """
        current_position = self.sprite.rect.center
        if current_position != destination:
            x, y = utils.geom.vectorize(current_position, destination)
            self.sprite.rect.move_ip(x, y)

    def move(self, destination_offset) -> None:
        """
        Translate the unit by the given offset.
        Args:
            destination_offset: The translation offset to perform
        """
        self.sprite.rect.move_ip(destination_offset[0], destination_offset[1])
