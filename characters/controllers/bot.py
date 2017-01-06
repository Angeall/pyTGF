from abc import ABCMeta, abstractmethod

from characters.controller import Controller
from game.gamestate import GameState


class Bot(Controller, metaclass=ABCMeta):
    def __init__(self, player_number: int):
        """
       Instantiates a bot controller for a unit.

       Args:
           player_number: The identifier of the unit controlled by this controller
       """
        super().__init__(player_number)
        self._gameStateLocalCopy = None
        self.previousGameState = None

    @property
    def gameState(self):
        return self._gameStateLocalCopy

    @gameState.setter
    def gameState(self, value):
        if isinstance(value, GameState):
            self._gameStateLocalCopy = value

    def moveGameState(self, player_number: int, move_event):
        """
        Performs a move in the local copy of the game

        Args:
            player_number:
            move_event:
        """
        self.gameState.performMove(player_number, move_event)
        if self._isMoveInteresting():
            self._selectNewMove(self.gameState)

    @abstractmethod
    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        """
        Evaluates if the move that has been done must trigger a new move from this controller

        Args:
            player_number: The player that performed the given move
            new_move_event: The new game state, to compare to the previously handled game state

        Returns: True if the move must trigger a new move. False otherwise.
        """
        pass

    @abstractmethod
    def _selectNewMove(self, game_state: GameState):
        """
        Decision taking algorithm that, given the new game state, will (or won't if not needed) make a move in the game

        Args:
            game_state:
                The game state to react to. This game state must not be modified in place, in order to
                maintain a stable local copy of the game state.
        """
        pass
