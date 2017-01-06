from board.tile import Tile


WALL_COLOR = (125, 85, 7)


class Wall(Tile):
    def __init__(self, center: tuple, points: list, identifier: tuple, neighbours=None):
        super().__init__(center, points, identifier, False, False, neighbours)
        self.graphics.setInternalColor(WALL_COLOR)
