import os

from characters.sprite import UnitSprite

from pytgf.characters.units import MovingUnit


class BoxSprite(UnitSprite):
    @property
    def imageName(self):
        return os.path.join("sprites", "box.png")


class Box(MovingUnit):
    def __init__(self, speed: int, player_number: int=-1):
        super().__init__(player_number, BoxSprite(), speed=speed, surviving_particles=True)
        self.playerNumber = player_number
