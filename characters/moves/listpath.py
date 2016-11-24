from characters.moves.path import Path
from characters.moves.move import ShortMove
from utils.functions import DelayedFunction


class ListPath(Path):
    def __init__(self, move_list: list, pre_action: DelayedFunction=None, post_action: DelayedFunction=None):
        """
        Creates a path containing all the short moves to perform in the given list
        Args:
            move_list: The list containing all the moves for the path
        """
        super().__init__(pre_action, post_action)
        self.list = move_list
        self.index = 0

    def _getNextShortMove(self) -> ShortMove:
        if self.index < len(self.list):
            move = self.list[self.index]
            self.index += 1
            return move
        else:
            return None
