import os

from characters.sprite import UnitSprite

from pytgf.characters.units import MovingUnit


class SokobanPlayerSprite(UnitSprite):
    @property
    def imageName(self):
        return os.path.join("sprites", "player.png")


class SokobanDrawstick(MovingUnit):
    def __init__(self, speed: int, player_number: int):
        super().__init__(player_number, SokobanPlayerSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
