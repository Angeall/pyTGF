import os

from pytgf.characters.units import MovingUnit
from pytgf.characters.units.sprite import UnitSprite


class SokobanPlayerSprite(UnitSprite):
    @property
    def imageRelativePath(self):
        return os.path.join("sprites", "player.png")


class SokobanDrawstick(MovingUnit):
    def __init__(self, speed: int, player_number: int):
        super().__init__(player_number, SokobanPlayerSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
