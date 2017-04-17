import os

from pytgf.characters.units import Unit
from pytgf.characters.units.sprite import UnitSprite


class BoxSprite(UnitSprite):
    @property
    def imageRelativePath(self):
        return os.path.join(self.resFolder, "box.png")


class Box(Unit):
    def __init__(self, speed: int, id_number: int=-1):
        super().__init__(id_number, BoxSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = id_number
