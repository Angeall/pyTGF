from characters.moves.path import Path
from characters.moves.move import ShortMove
from characters.unit import Unit
from display.tile import Tile
from types import FunctionType as function


class ContinuousMove(Path):
    def __init__(self, unit: Unit, source_tile: Tile, next_tile_func: function, fps: int):
        """

        Args:
            source_tile:
            next_tile_func: function that, given a tile, gives another tile (e.g. SquareBoard.getLeftTile(tile))
            fps:
        """
        super().__init__()
        self.unit = unit
        self.sourceTile = source_tile
        self.nextTileFunc = next_tile_func
        self.fps = fps

    def _getNextShortMove(self) -> ShortMove:
        destination_tile = self.nextTileFunc(self.sourceTile)
        move = ShortMove(self.unit, self.sourceTile, destination_tile, self.fps)
        self.sourceTile = destination_tile
        return move
