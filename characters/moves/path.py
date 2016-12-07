from abc import ABCMeta, abstractmethod
from types import FunctionType as function

from characters.moves.move import ShortMove


class Path(metaclass=ABCMeta):
    def __init__(self, pre_action: function=None, post_action: function=None,
                 step_pre_action: function=None, step_post_action: function=None):
        """
        Instantiates a path, which is a series of ShortMoves
        Args:
            pre_action: The action to perform before the first move is performed
            post_action: The action to perform after the last move was performed
            step_pre_action: The action to perform each time a step (ShortMove) has been started.
            step_post_action: The action to perform each time a step (ShortMove) has been completed.
                (step actions can have an unfulfilled "previous_tile" parameter, which will be filled with the last tile
                 and an unfulfilled "current_tile" parameter, which will be filled with the new current tile)
        """
        self.cancelTriggered = False
        self.cancelled = False
        self.completed = False
        self._currentMove = None  # type: ShortMove
        self._preAction = pre_action  # type: function
        self._postAction = post_action  # type: function
        self._stepPreAction = step_pre_action  # type: function
        self._stepPostAction = step_post_action  # type: function
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
        self._handleFirstMove()
        if not self._pathFinished():
            if self._currentMove is None and self._isFirstMoveEmpty():
                return
            else:
                self._currentMove.performStep()
                if self._currentMove.isPerformed:
                    new_tile_id = self._handleStepFinished()
                    self._getNextStepIfNeeded()
                    return new_tile_id

    def _handleFirstMove(self):
        if self._isFirstMove:
            if self._preAction is not None:
                self._preAction()
                self._preAction = None
            self._isFirstMove = False

    def _isFirstMoveEmpty(self):
        self._currentMove = self._getNextShortMove()
        if self._currentMove is None:  # Empty case: getNextShortMove returns nothing => Stops directly
            self.completed = True
            return
        else:
            self._performAction(self._stepPreAction)

    def _pathFinished(self):
        return self.cancelled or self.completed

    def _handleStepFinished(self):
        """
        A step has been completed, handles it
        Returns: The new tile id the unit is now on
        """
        self._performAction(self._stepPostAction)
        return self._currentMove.destinationTile.identifier

    def _getNextStepIfNeeded(self):
        """
        Checks if the path is cancelled, otherwise, get its next step and performs the needed action
        Returns:

        """
        if self.cancelTriggered:
            self.cancelled = True
            self._handlePathFinished()
        else:
            self._currentMove = self._getNextShortMove()
            if self._currentMove is not None:
                self._performAction(self._stepPreAction)
            else:
                self.completed = True
                self._handlePathFinished()

    def _performAction(self, action):
        if action is not None:
            try:
                action(previous_tile=self._currentMove.sourceTile,
                       current_tile=self._currentMove.destinationTile)
            except TypeError:
                action()

    def _handlePathFinished(self):
        if self._postAction is not None:
            self._postAction()
            self._postAction = None

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
