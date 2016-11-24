from abc import ABCMeta, abstractmethod

from characters.moves.move import ShortMove
from utils.functions import DelayedFunction


class Path(metaclass=ABCMeta):
    def __init__(self, pre_action: DelayedFunction=None, post_action: DelayedFunction=None):
        self.cancelTriggered = False
        self.cancelled = False
        self.completed = False
        self._currentMove = None
        self._preAction = pre_action  # type: DelayedFunction
        self._postAction = post_action  # type: DelayedFunction
        self._isFirstMove = True

    def cancel(self, cancel_post_action: bool=True) -> None:
        """
        Triggers the cancellation protocol (the path is fully cancelled once the current short move is performed)
        """
        self.cancelTriggered = True
        if cancel_post_action:
            self._postAction = None

    def performNextMove(self):
        """
        Performs the next step in the path
        Returns: The id of the new tile of the unit, or None if the current move is not performed yet.
        """
        if self._isFirstMove:
            if self._preAction is not None:
                self._preAction.exec()
                self._preAction = None
            self._isFirstMove = False
        if not (self.cancelled or self.completed):
            if self._currentMove is None:
                self._currentMove = self._getNextShortMove()
                if self._currentMove is None:  # Empty case: getNextShortMove returns nothing => Stops directly
                    self.completed = True
                    return
            if self._currentMove.isPerformed:
                new_tile_id = self._currentMove.destinationTile.identifier
                if self.cancelTriggered:
                    self.cancelled = True
                else:
                    self._currentMove = self._getNextShortMove()
                    self._currentMove.performStep()
                return new_tile_id
            else:
                self._currentMove.performStep()
        else:
            if self._postAction is not None:
                self._postAction.exec()
                self._postAction = None

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
