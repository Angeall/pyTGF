import os

from pytgf.characters.units import MovingUnit
from pytgf.characters.units.sprite import UnitSprite


class BoxSprite(UnitSprite):
    @property
    def imageRelativePath(self):
        return os.path.join(self.resFolder, "box.png")


class Box(MovingUnit):
    def __init__(self, speed: int, player_number: int=-1):
        super().__init__(player_number, BoxSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
