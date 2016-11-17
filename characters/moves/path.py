from abc import ABCMeta, abstractmethod

from characters.moves.move import ShortMove


class Path(metaclass=ABCMeta):
    def __init__(self):
        self.cancelTriggered = False
        self.cancelled = False
        self.completed = False
        self._currentMove = None

    def cancel(self):
        self.cancelTriggered = True

    def performNextMove(self) -> None:
        if not (self.cancelled or self.completed):
            if self._currentMove is None:
                self._currentMove = self._getNextShortMove()
                if self._currentMove is None:  # Empty case: getNextShortMove returns nothing => Stops directly
                    self.completed = True
                    return
            if self._currentMove.isPerformed:
                if self.cancelTriggered:
                    self.cancelled = True
                else:
                    self._currentMove = self._getNextShortMove()
                    self._currentMove.performStep()

    @abstractmethod
    def _getNextShortMove(self) -> ShortMove:
        """
        Returns: The next move in the path or None if there is none
        """
        pass
