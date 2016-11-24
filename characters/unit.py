import pygame

import utils.geom
from characters.sprite import UnitSprite


class Unit(object):
    # TODO: make a controller for each unit. The controller will be the API call
    def __init__(self, sprite: UnitSprite, speed: float = 150):
        """
        Instantiates a character unit in the game
        Args:
            sprite: The sprite to draw on the board
            speed: The speed, in pixels per seconds, of the unit when moving
        """
        self.sprite = sprite  # type: UnitSprite
        self.group = None
        self.speed = speed
        self.currentAction = None

    def drawAsSingleSprite(self, surface: pygame.Surface):
        if self.group is None:
            self.group = pygame.sprite.RenderPlain(self.sprite)
        self.group.draw(surface)

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
        print("moving")
        self.sprite.rect.move_ip(destination_offset[0], destination_offset[1])
