import os

from characters.sprite import UnitSprite
from characters.units.moving_unit import MovingUnit


class PlayerSprite(UnitSprite):
    @property
    def imageName(self):
        return os.path.join("sprites", "player.png")


class Player(MovingUnit):
    def __init__(self, speed: int, player_number: int):
        super().__init__(player_number, PlayerSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
