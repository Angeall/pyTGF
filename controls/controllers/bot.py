from abc import ABCMeta, abstractmethod

from controls.controller import Controller
from controls.events.bot import BotEvent
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

    def reactToEvent(self, event: BotEvent):
        """
        Performs a move in the local copy of the game

        Args:
            event: The event that contains the move to perform in the local copy of the game
        """
        self.gameState.performMove(event.playerNumber, event.moveDescriptor)
        if self._isMoveInteresting(event.playerNumber, event.moveDescriptor):
            self._selectNewMove(self.gameState)

    @abstractmethod
    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        """
        Evaluates if the move that has been done must trigger a new move from this controller

        Args:
            player_number: The player that performed the given move
            new_move_event: The new move performed

        Returns: True if the move must trigger a new move. False otherwise.
        """
        pass

    @abstractmethod
    def _selectNewMove(self, game_state: GameState):
        """
        Decision taking algorithm that, given the new game state, will (or won't if not needed) make a move in the game
        Returns nothing ! Just add a new move in the moves Queue

        Args:
            game_state:
                The game state to react to. This game state must not be modified in place, in order to
                maintain a stable local copy of the game state.
        """
        pass
