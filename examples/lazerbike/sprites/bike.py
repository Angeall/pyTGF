from characters.sprite import UnitSprite
from characters.unit import Unit


class BikeSprite(UnitSprite):
    @property
    def imageName(self) -> str:
        return "bike.png"


class Bike(Unit):
    def __init__(self, sprite: UnitSprite, initial_direction: int):
        super().__init__(sprite)
        self.direction = 0  # The initial position of the sprite is towards right
        self.turn(initial_direction)

    def turn(self, direction: int):
        angle = (direction - self.direction) * 90
        self.direction = direction
        self.sprite.rotate(angle)


