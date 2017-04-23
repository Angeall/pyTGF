"""
File containing the abstract definition of a Path. While the path has a next move, it continues.
"""
from abc import ABCMeta, abstractmethod
from typing import Optional, Callable, Tuple, Union

from .shortmove import ShortMove
from ..units import Particle
from ...board import Tile, TileIdentifier

__author__ = 'Anthony Rouneau'


class Path(metaclass=ABCMeta):
    """
    Class defining a Path, made of multiple moves, that can trigger actions at the beginning or the end of the path,
    and at the beginning or the end of a step in the path. When there is no move left in the path, the path ends.
    """

    def __init__(self, unit: Particle, pre_action: Optional[Callable[[], None]]=None,
                 post_action: Optional[Callable[[], None]]=None,
                 step_pre_action: Optional[Callable[[Tile, Tile], None]]=None,
                 step_post_action: Optional[Callable[[Tile, Tile], None]]=None, max_moves: int=-1):
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
        self.reachedTileIdentifier = None
        self.unit = unit
        self._currentMove = None  # type: ShortMove
        self._preAction = pre_action
        self._postAction = post_action
        self._stepPreAction = step_pre_action
        self._stepPostAction = step_post_action
        self._isFirstMove = True
        self._movesToGo = max_moves
        self._first = True
        self._needNextMove = False
        self._newMoveStarted = False
        self._newMoveTileId = None

    # -------------------- PUBLIC METHODS -------------------- #

    def stop(self, cancel_post_action: bool=True) -> None:
        """
        Triggers the cancellation protocol (the path is fully cancelled once the current short move is performed)
        """
        self.stopTriggered = True
        if cancel_post_action:
            self._postAction = None

    def finished(self):
        """
        Returns: True if this Path is finished, False otherwise
        """
        return self.stopped or self.completed

    def performNextMove(self) -> Tuple[bool, bool, Union[None, TileIdentifier]]:
        """
        Performs the next step in the path

        Returns:
            A tuple containing

                - True if the step just began, False otherwise
                - True if the step just finished, False otherwise
                - The id of the new tile of the unit, or None if the current move did not just start.
        """
        self._handleFirstMove()
        if not self.finished():
            if self._currentMove is None and self._isFirstMoveEmpty():
                self.completed = True
            else:
                if not self._currentMove.unit.isAlive():
                    self.stopped = True
                else:
                    move_just_started = self._newMoveStarted
                    self._newMoveStarted = False
                    new_tile_id = None
                    self._needNextMove = False
                    self._currentMove.performStep()
                    move_performed = self._currentMove.isPerformed
                    if move_just_started:
                        new_tile_id = self._newMoveTileId
                    if move_performed:
                        new_tile_id = self._handleStepFinished()
                        self.reachedTileIdentifier = new_tile_id
                        next_step_got, next_destination_tile_id = self._getNextStepIfNeeded()
                        self._newMoveStarted = next_step_got
                        self._newMoveTileId = next_destination_tile_id
                        self._decrementMovesToGo()
                    return move_just_started, move_performed, new_tile_id
        return False, False, None

    def complete(self) -> TileIdentifier:
        """
        Completes the Path until it reaches the end.

        Returns:
            The identifier of the tile on which the unit is located at the end of this Path.
        """
        tile_id = None
        while not self.finished():
            _, _, new_tile_id = self.performNextMove()
            if new_tile_id is not None:
                tile_id = new_tile_id
        return tile_id

    # -------------------- PROTECTED METHODS -------------------- #

    def _decrementMovesToGo(self):
        self._movesToGo -= 1
        if self._movesToGo == 0:
            self.stopped = True
            self._handlePathFinished()

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
            self._newMoveTileId = self._currentMove.destinationTile
            self._newMoveStarted = True
        return False

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
        self._first = False
        if self.stopTriggered:
            self.stopped = True
            self._handlePathFinished()
        else:
            self._currentMove = self._getNextConsistentMove()
            if self._currentMove is not None:
                self._performAction(self._stepPreAction)
                return True, self._currentMove.destinationTile
            else:
                self.completed = True
                self._handlePathFinished()
        return False, None

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

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
