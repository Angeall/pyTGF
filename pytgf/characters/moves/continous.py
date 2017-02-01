from types import FunctionType as function

from pytgf.characters.moves import ShortMove, Path
from pytgf.characters.units import MovingUnit


class ContinuousPath(Path):
    def __init__(self, unit: MovingUnit, source_tile_func: function, next_tile_func: function,
                 fps: int, units_location_dict: dict, pre_action: function=None, post_action: function=None,
                 step_pre_action: function=None, step_post_action: function=None, max_moves: int=-1):
        """
        Args:
            unit: The unit to move
            source_tile_func: function that, given a unit, gives its current tile
            next_tile_func: function that, given a tile, gives another tile (e.g. SquareBoard.getLeftTile(tile))
            fps: The screen refresh speed
            units_location_dict: The dictionary linking units to tile identifiers.
            pre_action: The action to perform before the first move is performed
            post_action: The action to perform after the last move was performed
            step_pre_action: The action to perform each time a step (ShortMove) has been started.
            step_post_action:
                The action to perform each time a step (ShortMove) has been completed.
                (step actions can have an unfulfilled "previous_tile" parameter, which will be filled with the last tile
                and an unfulfilled "current_tile" parameter, which will be filled with the new current tile)
            max_moves: The maximum number of moves done by the move to create (default: -1 => no limitations)
        """
        super().__init__(pre_action=pre_action, post_action=post_action, step_pre_action=step_pre_action,
                         step_post_action=step_post_action, max_moves=max_moves)
        self.unit = unit
        self.sourceTile = None
        self.nextTileFunc = next_tile_func
        self.sourceTileFunc = source_tile_func
        self._unitsLocationDict = units_location_dict
        self.fps = fps

    def _getNextShortMove(self) -> ShortMove:
        if self.sourceTile is None:
            self.sourceTile = self.sourceTileFunc(self.unit)
        if self.sourceTile is not None and self.sourceTile.identifier is not None:
            destination_tile = self.nextTileFunc(self.sourceTile)
            if destination_tile is not None and self.sourceTile is not destination_tile:
                move = ShortMove(self.unit, self.sourceTile, destination_tile, self.fps,
                                 units_location=self._unitsLocationDict)
                self.sourceTile = destination_tile
                return move
