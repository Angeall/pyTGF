import os

from pytgf.characters.units import MovingUnit
from pytgf.characters.units.sprite import UnitSprite


class DiscSprite(UnitSprite):
    def __init__(self, player_number: int, graphics: bool=True):
        super().__init__(graphics)
        self.playerNumber = player_number


    @property
    def imageRelativePath(self) -> str:
        return os.path.join(self.resFolder, "disc" + str(self.playerNumber) + ".png")


class Disc(MovingUnit):
    def __init__(self, player_number: int, graphics: bool=True):
        super().__init__(player_number=player_number, sprite=DiscSprite(player_number, graphics))