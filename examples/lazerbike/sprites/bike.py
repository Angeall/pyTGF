from characters.sprite import UnitSprite


class BikeSprite(UnitSprite):
    @property
    def imageName(self) -> str:
        return "bike.png"
