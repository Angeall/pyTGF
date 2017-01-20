from types import FunctionType as function

from characters.moves.path import Path
from characters.moves.move import ShortMove


class ListPath(Path):
    def __init__(self, move_list: list, pre_action: function=None, post_action: function=None,
                 step_pre_action: function = None, step_post_action: function = None, max_moves: int=-1):
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
        super().__init__(pre_action, post_action, step_pre_action, step_post_action, max_moves=max_moves)
        self.list = move_list
        self.index = 0

    def _getNextShortMove(self) -> ShortMove:
        if self.index < len(self.list):
            move = self.list[self.index]  # type: ShortMove
            self.index += 1
            return move
