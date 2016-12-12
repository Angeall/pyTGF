from display.tile import Tile
from examples.sokoban.units.box import Box


DEADLY_COLOR = (0, 0, 0)
OK_COLOR = (255, 0, 0)


class Hole(Tile):
    def __init__(self, center: tuple, points: list, identifier):
        super().__init__(center, points, identifier, True, True)
        self.setInternalColor(DEADLY_COLOR)

    def addOccupant(self, new_occupant):
        super().addOccupant(new_occupant)
        if isinstance(new_occupant, Box):
            self.deadly = False
            self.setInternalColor(OK_COLOR)
