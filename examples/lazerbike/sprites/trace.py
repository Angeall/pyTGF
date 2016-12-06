import os
import pygame
import pygame.transform as transform

from characters.particle import Particle
from characters.sprite import UnitSprite
from examples.lazerbike.controls.allowed_moves import *

TOP_RIGHT = 0
TOP_LEFT = 1
BOTTOM_LEFT = 2
BOTTOM_RIGHT = 3


def _getDirectionChangeType(previous_direction, current_direction):
    if previous_direction == GO_UP:
        print("previous: up")
        if current_direction == GO_LEFT:
            print("current: left")
            return BOTTOM_LEFT
        elif current_direction == GO_RIGHT:
            print("current: right")
            return BOTTOM_RIGHT
    elif previous_direction == GO_LEFT:
        print("previous: left")
        if current_direction == GO_UP:
            print("current: up")
            return TOP_RIGHT
        elif current_direction == GO_DOWN:
            print("current: down")
            return BOTTOM_RIGHT
    elif previous_direction == GO_RIGHT:
        print("previous: right")
        if current_direction == GO_UP:
            print("current: up")
            return TOP_LEFT
        elif current_direction == GO_DOWN:
            print("current: down")
            return BOTTOM_LEFT
    elif previous_direction == GO_DOWN:
        print("previous: down")
        if current_direction == GO_LEFT:
            print("current: left")
            return TOP_LEFT
        elif current_direction == GO_RIGHT:
            print("current: right")
            return TOP_RIGHT


class InvalidPlayerNumberException(BaseException):
    pass


class TraceSprite(UnitSprite):
    def __init__(self, player_number: int):
        if not 1 <= player_number <= 4:
            raise InvalidPlayerNumberException("Cannot create Player " + str(player_number))
        self._playerNumber = str(player_number)
        super().__init__()

    @property
    def imageName(self):
        return os.path.join("sprites", "trace" + self._playerNumber + ".png")

    def makeAngle(self, previous_direction: int, current_direction: int, background_color) -> None:
        """
        Make the trace an angle
        Args:
            background_color: The background color of the board
            previous_direction: The previous allowed move
            current_direction: The current allowed move
        """
        rotation_type = _getDirectionChangeType(previous_direction, current_direction)
        if self.rect.width > self.rect.height:  # Makes sure the trace is vertical
            self.rotate(90)
        half_height = int(round(self.rect.height/2))
        bottom_half_surface = pygame.Surface((half_height, half_height))
        bottom_half_surface.fill(background_color)
        bottom_half_surface.blit(self.image, (0, 0))
        # self.image = bottom_half_surface
        # self.rect = self.image.get_rect()
        bottom_half_surface = transform.rotate(bottom_half_surface, 90)
        #self.image = transform.chop(self.image, bottom_half_rect)
        bottom_half_surface.blit(self.image, (0, 0))
        self.image = bottom_half_surface
        self.rect = self.image.get_rect()
        # print("rotation")
        print(rotation_type)
        self.rotate(rotation_type*90)
        # print("finished rotation")


class Trace(Particle):
    def __init__(self, player_number: int):
        super().__init__(sprite=TraceSprite(player_number))
        self.playerNumber = player_number

