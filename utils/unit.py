from gameboard.tile import Tile
from characters.units.unit import Unit
from utils.geom import get_hypotenuse_length, get_polygon_radius


def resize_unit(unit: Unit, tile: Tile) -> None:
    """
    Resize a unit to fit the given tile
    Args:
        unit: The unit to resize
        tile: The tile to fit in
    """
    if tile.graphics is not None:
        multiply_ratio = tile.graphics.sideLength / max(unit.sprite.rect.height, unit.sprite.rect.width)
        hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                           unit.sprite.rect.width * multiply_ratio)
        tile_diameter = get_polygon_radius(tile.graphics.nbrOfSides, tile.graphics.sideLength) * 2
        while hypotenuse > tile_diameter:
            multiply_ratio *= 0.99
            hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                               unit.sprite.rect.width * multiply_ratio)
        unit.sprite.size(int(round(unit.sprite.rect.width * multiply_ratio)),
                         int(round(unit.sprite.rect.height * multiply_ratio)))