from board.tile import Tile


WALL_COLOR = (125, 85, 7)


class Wall(Tile):
    def __init__(self, center: tuple, points: list, identifier):
        super().__init__(center, points, identifier, False, False)
        self.setInternalColor(WALL_COLOR)
