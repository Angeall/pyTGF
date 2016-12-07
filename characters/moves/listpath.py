from types import FunctionType as function

from characters.moves.path import Path
from characters.moves.move import ShortMove


class ListPath(Path):
    def __init__(self, move_list: list, pre_action: function=None, post_action: function=None,
                 step_pre_action: function = None, step_post_action: function = None):
        """
        Creates a path containing all the short moves to perform in the given list
        Args:
            move_list: The list containing all the moves for the path
            pre_action: The action to perform before the first move is performed
            post_action: The action to perform after the last move was performed
            step_pre_action: The action to perform each time a step (ShortMove) has been started.
            step_post_action:
                The action to perform each time a step (ShortMove) has been completed.
                (step actions can have an unfulfilled "previous_tile" parameter, which will be filled with the last tile
                and an unfulfilled "current_tile" parameter, which will be filled with the new current tile)
        """
        super().__init__(pre_action, post_action, step_pre_action, step_post_action)
        self.list = move_list
        self.index = 0

    def _getNextShortMove(self) -> ShortMove:
        if self.index < len(self.list):
            move = self.list[self.index]
            self.index += 1
            return move
        else:
            return None
