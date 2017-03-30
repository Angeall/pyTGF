import os

from pytgf.characters.units import MovingUnit
from pytgf.characters.units.sprite import UnitSprite

default_player_number = 1


class InvalidPlayerNumberException(BaseException):
    pass


class BikeSprite(UnitSprite):
    def __init__(self, player_number: int, graphics: bool=True):
        if not 1 <= player_number <= 4:
            raise InvalidPlayerNumberException("Cannot create Player " + str(player_number))
        self.playerNumber = str(player_number)
        super().__init__(graphics)

    @property
    def imageRelativePath(self) -> str:
        return os.path.join(self.resFolder, "bike" + self.playerNumber + ".png")


class Bike(MovingUnit):
    def __init__(self, speed: int, player_number: int=default_player_number, max_trace: int=-1, initial_direction=0,
                 graphics: bool=True):
        global default_player_number
        super().__init__(player_number, BikeSprite(player_number, graphics=graphics), max_particles=max_trace,
                         speed=speed, surviving_particles=True)
        default_player_number += 1
        self.playerNumber = player_number
        self.lastAction = 0
        if initial_direction != 0:
            self.turn(initial_direction)

    def turn(self, direction: int):
        angle = (direction - self.lastAction) * 90
        self.sprite.rotate(angle)
        self.lastAction = direction


