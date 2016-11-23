from abc import ABCMeta, abstractmethod

from characters.moves.move import ShortMove


class Path(metaclass=ABCMeta):
    def __init__(self):
        self.cancelTriggered = False
        self.cancelled = False
        self.completed = False
        self._currentMove = None

    def cancel(self) -> None:
        """
        Triggers the cancellation protocol (the path is fully cancelled once the current short move is performed)
        """
        self.cancelTriggered = True

    def performNextMove(self):
        """
        Perform the next step in the path
        Returns: The id of the new tile of the unit, or None if the current move is not performed yet.
        """
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

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
