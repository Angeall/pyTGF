from characters.controller import Controller
from abc import ABCMeta, abstractmethod

from game.gamestate import GameState


class Bot(Controller, metaclass=ABCMeta):
    def __init__(self, player_number: int):
        """
       Instantiates a bot controller for a unit.
       Args:
           player_number: The identifier of the unit controlled by this controller
       """
        super().__init__(player_number)
        self.previousGameState = None

    def reactToGameState(self, game_state: GameState):
        if not self._isGameStateAlreadyHandled(game_state):
            self._reactToNewGameState(game_state)
            self.previousGameState = game_state
        return 1

    @abstractmethod
    def _isGameStateAlreadyHandled(self, game_state: GameState) -> bool:
        """
        Compares the given state with the previously handled rules state and returns if they are equal
        to one another or not.
        Please note that the first "previous_state" will be None.
        Attention : this method must be efficient because it will be called frequently.

        Args:
            game_state: The new rules state, to compare to the previously handled rules state

        Returns: True if the two rules states are similar (hence, the "new" rules state has no reason to be handled again)
                 False otherwise, which will trigger the decision-taking algorithm
        """
        pass

    @abstractmethod
    def _reactToNewGameState(self, game_state: GameState):
        """
        Decision taking algorithm that, given the new rules state, will (or won't if not needed) make a move in the rules

        Args:
            game_state: The new rules state to react to
        """
        pass
