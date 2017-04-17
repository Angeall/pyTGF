import os

from pytgf.characters.units import Particle
from pytgf.characters.units.sprite import UnitSprite


class DiscSprite(UnitSprite):
    def __init__(self, team_number: int, graphics: bool=True):
        self.teamNumber = team_number
        super().__init__(graphics)

    @property
    def imageRelativePath(self) -> str:
        return os.path.join(self.resFolder, "disc" + str(self.teamNumber) + ".png")


class Disc(Particle):
    def __init__(self, player_number: int, team_number: int, speed: int,  graphics: bool=True):
        super().__init__(id_number=player_number, sprite=DiscSprite(team_number, graphics), speed=speed)
