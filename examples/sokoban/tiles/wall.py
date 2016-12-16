from board.tile import Tile


WALL_COLOR = (53, 35, 3)


class Wall(Tile):
    def __init__(self, center: tuple, points: list, identifier):
        super().__init__(center, points, identifier, False, False)
        self.setInternalColor(WALL_COLOR)
