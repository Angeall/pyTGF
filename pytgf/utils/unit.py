from gameboard.board import Board
from utils.geom import get_hypotenuse_length, get_polygon_radius

from pytgf.characters.units import Unit


def resize_unit(unit: Unit, board: Board) -> None:
    """
    Resize a unit to fit a tile of the given board

    Args:
        unit: The unit to resize
        board: The board on which the tile of the unit is located
    """
    if board.graphics is not None:
        multiply_ratio = board.graphics.sideLength / max(unit.sprite.rect.height, unit.sprite.rect.width)
        hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                           unit.sprite.rect.width * multiply_ratio)
        tile_diameter = get_polygon_radius(board.graphics.nbrOfSides, board.graphics.sideLength) * 2
        while hypotenuse > tile_diameter:
            multiply_ratio *= 0.99
            hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                               unit.sprite.rect.width * multiply_ratio)
        unit.sprite.size(int(round(unit.sprite.rect.width * multiply_ratio)),
                         int(round(unit.sprite.rect.height * multiply_ratio)))
