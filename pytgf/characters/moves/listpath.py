"""
File containing the definition of a path made of a list of ShortMoves
"""

from typing import List, Optional, Callable

from pytgf.board import Tile
from pytgf.characters.moves.path import Path
from pytgf.characters.moves.shortmove import ShortMove
from pytgf.characters.units import Particle

__author__ = 'Anthony Rouneau'


class ListPath(Path):
    """
    Class defining a path made of a list os ShortMoves. When the path reaches the end of that list,
    the path is considered as finished
    """
    def __init__(self, unit: Particle, move_list: List[ShortMove], pre_action: Optional[Callable[[], None]]=None,
                 post_action: Optional[Callable[[], None]]=None,
                 step_pre_action: Optional[Callable[[Tile, Tile], None]]=None,
                 step_post_action: Optional[Callable[[Tile, Tile], None]]=None, max_moves: int=-1):
        """
        Creates a path containing all the short moves to perform in the given list
        Args:
            move_list: The list containing all the moves (of type 'ShortMove') for the path
            pre_action: The action to perform before the first move is performed
            post_action: The action to perform after the last move was performed
            step_pre_action: The action to perform each time a step (ShortMove) has been started.
            step_post_action:
                The action to perform each time a step (ShortMove) has been completed.
                (step actions can have an unfulfilled "previous_tile" parameter, which will be filled with the last tile
                and an unfulfilled "current_tile" parameter, which will be filled with the new current tile)
            max_moves: The maximum number of moves done by the move to create (default: -1 => no limitations)
        """
        super().__init__(unit, pre_action, post_action, step_pre_action, step_post_action, max_moves=max_moves)
        self.list = move_list
        self.index = 0

    # -------------------- PROTECTED METHODS -------------------- #

    def _getNextShortMove(self) -> ShortMove:
        if self.index < len(self.list):
            move = self.list[self.index]
            self.index += 1
            return move
