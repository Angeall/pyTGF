from gameboard.tile import Tile
from examples.sokoban.units.box import Box


DEADLY_COLOR = (0, 0, 0)
OK_COLOR = (125, 125, 125)


class Hole(Tile):
    def __init__(self, center: tuple, points: list, identifier: tuple, neighbours=None):
        super().__init__(center, points, identifier, True, True, neighbours)
        self.graphics.setInternalColor(DEADLY_COLOR)

    def addOccupant(self, new_occupant):
        super().addOccupant(new_occupant)
        if isinstance(new_occupant, Box):
            self.deadly = False
            self.graphics.setInternalColor(OK_COLOR)
