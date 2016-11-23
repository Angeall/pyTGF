from characters.moves.path import Path
from characters.moves.move import ShortMove
from characters.unit import Unit
from display.tile import Tile
from types import FunctionType as function


class ContinuousMove(Path):
    def __init__(self, unit: Unit, source_tile_func: function, next_tile_func: function, fps: int):
        """

        Args:
            source_tile: function that, given a unit, gives its current tile
            next_tile_func: function that, given a tile, gives another tile (e.g. SquareBoard.getLeftTile(tile))
            fps:
        """
        super().__init__()
        self.unit = unit
        self.sourceTile = None
        self.nextTileFunc = next_tile_func
        self.sourceTileFunc = source_tile_func
        self.fps = fps

    def _getNextShortMove(self) -> ShortMove:
        if self.sourceTile is None:
            self.sourceTile = self.sourceTileFunc(self.unit)
        destination_tile = self.nextTileFunc(self.sourceTile)
        move = ShortMove(self.unit, self.sourceTile, destination_tile, self.fps)
        self.sourceTile = destination_tile
        return move
