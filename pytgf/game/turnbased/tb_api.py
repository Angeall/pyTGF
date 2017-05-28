from abc import ABCMeta

from ..api import API
from ..core import Core
from ...characters.moves import MoveDescriptor, Path


class NotYourTurnException(Exception):
    pass


class TurnBasedAPI(API, metaclass=ABCMeta):

    def __init__(self, game: Core):
        super().__init__(game)
        self.currentPlayerIndex = 0

    def performMove(self, player_number: int, move_descriptor: MoveDescriptor, force: bool = False):
        if self.game.isFinished():
            return True
        if not force and player_number != self.getCurrentPlayer():
            raise NotYourTurnException("The move is performed by player " + str(player_number) + " while the current "
                                       "player is " + str(self.getCurrentPlayer()))
        return super().performMove(player_number, move_descriptor, force)

    def isCurrentPlayer(self, player_number: int) -> bool:
        """
        Args:
            player_number: The number representing the player 

        Returns: True if the given player is the current player in the turn by turn game 
        """
        return self.getCurrentPlayer() == player_number

    def getPlayerNumbersInOrder(self):
        """
        
        Returns: The numbers representing the players, ordered by the playing order

        """
        return self.game.playerNumbers

    def getCurrentPlayer(self) -> int:
        """
        Returns: The number representing the current player
        """
        return self.game.playerNumbers[self.currentPlayerIndex]

    def switchToNextPlayer(self):
        """
        Returns: The number representing the current player
        """
        self.currentPlayerIndex = self._getNextPlayerIndex()

    def getNextPlayer(self, offset: int = 1) -> int:
        """
        Get the number of the next player (the player that plays after "offset" turns)

        Args:
            offset: The number of turns that must be played before the returned player can play 

        Returns: The number of the player that will play in "offset" turns
        """
        return self.game.playerNumbers[self._getNextPlayerIndex(offset)]

    def _getNextPlayerIndex(self, offset: int = 1) -> int:
        """
        Get the index (to be matched with the playerNumbers list) of the next player (
        the player that plays after "offset" turns)

        Args:
            offset: The number of turns that must be played before the returned player can play 

        Returns: The index of the player that will play in "offset" turns
        """
        next_player_index = (self.currentPlayerIndex + offset) % len(self.game.playerNumbers)
        next_player_number = self.game.playerNumbers[next_player_index]
        while not self.isFinished() and not self.isPlayerAlive(next_player_number):
            next_player_index = (next_player_index + 1) % len(self.game.playerNumbers)
            if next_player_index == self.currentPlayerIndex:
                break
            next_player_number = self.game.playerNumbers[next_player_index]
        return next_player_index

    def _mustCheckIfFinishedAfterSimulations(self) -> bool:
        return False

    def _reactToMovePerformed(self, player_number: int, move: Path):
        self.switchToNextPlayer()
        self.game.checkIfFinished()

    def _getSequenceOfPlayerNumbers(self):
        player_numbers = [self.getCurrentPlayer()]
        for i in range(1, len(self.getAlivePlayersNumbers())):
            player_numbers.append(self.getNextPlayer(offset=i))
        return player_numbers
