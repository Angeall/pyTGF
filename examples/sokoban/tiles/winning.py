from board.tile import Tile
from examples.sokoban.units.box import Box


COLOR = (0, 255, 0)


class Winning(Tile):
    def __init__(self, center: tuple, points: list, identifier: tuple, neighbours=None):
        super().__init__(center, points, identifier, True, False, neighbours)
        self.graphics.setInternalColor(COLOR)
