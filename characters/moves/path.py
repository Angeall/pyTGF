from abc import ABCMeta, abstractmethod
from types import FunctionType as function

import sys

from characters.moves.move import ShortMove


class Path(metaclass=ABCMeta):
    def __init__(self, pre_action: function=None, post_action: function=None,
                 step_pre_action: function=None, step_post_action: function=None, max_moves: int=-1):
        """
        Instantiates a path, which is a series of ShortMoves

        Args:
            pre_action: The action to perform before the first move is performed
            post_action: The action to perform after the last move was performed
            step_pre_action: The action to perform each time a step (ShortMove) has been started.
            step_post_action:
                The action to perform each time a step (ShortMove) has been completed.
                (step actions can have an unfulfilled "previous_tile" parameter, which will be filled with the last tile
                and an unfulfilled "current_tile" parameter, which will be filled with the new current tile)
            max_moves: The maximum number of moves done by the move to create (default: -1 => no limitations)
        """
        self.stopTriggered = False
        self.stopped = False
        self.completed = False
        self._currentMove = None  # type: ShortMove
        self._preAction = pre_action  # type: function
        self._postAction = post_action  # type: function
        self._stepPreAction = step_pre_action  # type: function
        self._stepPostAction = step_post_action  # type: function
        self._isFirstMove = True
        self._movesToGo = max_moves

    def stop(self, cancel_post_action: bool=True) -> None:
        """
        Triggers the cancellation protocol (the path is fully cancelled once the current short move is performed)
        """
        self.stopTriggered = True
        if cancel_post_action:
            self._postAction = None

    def performNextMove(self):
        """
        Performs the next step in the path
        Returns: The id of the new tile of the unit, or None if the current move is not performed yet.
        """
        self._handleFirstMove()
        if not self.finished():
            if self._currentMove is None and self._isFirstMoveEmpty():
                self.completed = True
                return
            else:
                if not self._currentMove.unit.isAlive():
                    self.stopped = True
                else:
                    self._currentMove.performStep()
                    if self._currentMove.isPerformed:

                        new_tile_id = self._handleStepFinished()
                        self._getNextStepIfNeeded()
                        self._movesToGo -= 1
                        if self._movesToGo == 0:
                            self.stopped = True
                            self._handlePathFinished()
                        return new_tile_id

    def _handleFirstMove(self):
        if self._isFirstMove:
            if self._preAction is not None:
                self._preAction()
                self._preAction = None
            self._isFirstMove = False

    def _isFirstMoveEmpty(self):
        self._currentMove = self._getNextConsistentMove()
        if self._currentMove is None:  # Empty case: getNextShortMove returns nothing => Stops directly
            return True
        else:
            self._performAction(self._stepPreAction)
        return False

    def finished(self):
        return self.stopped or self.completed

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
        if self.stopTriggered:
            self.stopped = True
            self._handlePathFinished()
        else:
            self._currentMove = self._getNextConsistentMove()
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

    def _getNextConsistentMove(self):
        """
        Makes sure the next considered move is consistent (i.e. correct)

        Returns: The move, with the guarantee it is either a correct move or it is None
        """
        current_move = None
        consistent_move = False
        while not consistent_move:
            current_move = self._getNextShortMove()
            consistent_move = current_move is None or current_move.isConsistent()
        return current_move

    def complete(self) -> tuple:
        tile_id = None
        while not self.finished():
            tile_id = self.performNextMove()
        return tile_id

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
