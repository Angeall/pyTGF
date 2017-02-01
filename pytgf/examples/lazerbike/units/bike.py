import os

from characters.sprite import UnitSprite

from pytgf.characters.units import MovingUnit

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
    def __init__(self, speed: int, player_number: int=default_player_number, max_trace: int=-1, initial_direction=0):
        global default_player_number
        super().__init__(player_number, BikeSprite(player_number), max_particles=max_trace, speed=speed,
                         surviving_particles=True)
        default_player_number += 1
        self.playerNumber = player_number
        self.currentAction = 0  # The initial position of the sprite is towards right
        self.turn(initial_direction)

    def turn(self, direction: int):
        angle = (direction - self.currentAction) * 90
        self.currentAction = direction
        self.sprite.rotate(angle)


