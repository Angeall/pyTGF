import os

from ....characters.units import Unit
from ....characters.units.sprite import UnitSprite


class SokobanPlayerSprite(UnitSprite):
    @property
    def imageRelativePath(self):
        return os.path.join(self.resFolder, "player.png")


class SokobanDrawstick(Unit):
    def __init__(self, speed: int, player_number: int):
        super().__init__(player_number, SokobanPlayerSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
