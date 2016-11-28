from characters.sprite import UnitSprite
from characters.units.moving_unit import MovingUnit

import os


default_player_number = 1


class InvalidPlayerNumberException(BaseException):
    pass


class BikeSprite(UnitSprite):
    def __init__(self, player_number: int):
        if not 1 <= player_number <= 4:
            raise InvalidPlayerNumberException("Cannot create Player " + str(player_number))
        self.playerNumber = str(player_number)
        super().__init__()

    @property
    def imageName(self) -> str:
        return os.path.join("sprites", "bike" + self.playerNumber + ".png")


class Bike(MovingUnit):
    def __init__(self, player_number: int=default_player_number, max_trace: int=-1):
        global default_player_number
        super().__init__(BikeSprite(player_number), max_particles=max_trace)
        default_player_number += 1
        self.playerNumber = player_number
        self.direction = 0  # The initial position of the sprite is towards right
        # self.turn(initial_direction)

    def turn(self, direction: int):
        angle = (direction - self.direction) * 90
        self.direction = direction
        self.sprite.rotate(angle)


