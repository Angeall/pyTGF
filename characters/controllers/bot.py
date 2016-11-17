from characters.controller import Controller
from abc import ABCMeta, abstractmethod


class Bot(Controller, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self.previousGameState = None

    def reactToGameState(self, game_state):
        if not self._isGameStateHandled(game_state):
            self._reactToNewGameState(game_state)
            self.previousGameState = game_state

    @abstractmethod
    def _isGameStateHandled(self, game_state) -> bool:
        """
        Compares the given state with the previously handled game state and returns if they are equal
        to one another or not.
        Please note that the first "previous_state" will be None.
        Attention : this method must be efficient because it will be called very frequently.
        Attention : this method must be efficient because it will be called very frequently.
        Args:
            game_state: The new game state, to compare to the previously handled game state

        Returns: True if the two game states are similar (hence, the "new" game state has no reason to be handled again)
                 False otherwise, which will trigger the decision-taking algorithm
        """
        pass

    @abstractmethod
    def _reactToNewGameState(self, game_state) -> None:
        """
        Decision taking algorithm that, given the new game state, will (or won't if not needed) make a move in the game
        Args:
            game_state: The new game state to react to
        """
        pass
