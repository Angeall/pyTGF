import traceback
from abc import ABCMeta, abstractmethod
from queue import Queue
from typing import List

from controls.controller import Controller
from controls.events.bot import BotEvent
from game.game import Game
from game.gamestate import GameState


class TeammatePayload:
    def __init__(self, teammate_number: int, message):
        self.teammateNumber = teammate_number
        self.message = message


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
        self.messagesToTeammates = Queue()

    @property
    def gameState(self):
        return self._gameStateLocalCopy

    @gameState.setter
    def gameState(self, game: Game):
        if isinstance(game, Game):
            self._gameStateLocalCopy = self._getGameStateAPI(game)

    def reactToEvents(self, events: List[BotEvent]):
        """
        Performs a move in the local copy of the game

        Args:
            events: list of events, each member contains the move to perform in the local copy of the game
        """
        move_interesting = False
        for event in events:  # type: BotEvent
            try:
                succeeded = self.gameState.performMove(event.playerNumber, event.moveDescriptor)
                if not succeeded:
                    print("error in move... for player %s and descriptor %s" %
                          (str(event.playerNumber), str(event.moveDescriptor)))

                move_interesting = move_interesting or self._isMoveInteresting(event.playerNumber, event.moveDescriptor)
            except:
                traceback.print_exc()
        if move_interesting:
            selected_move = self._selectNewMove(self.gameState)
            if self._isMoveAllowed(selected_move):
                self.moves.put(selected_move)

    def sendMessageToTeammate(self, teammate_number: int, message):
        """
        Adds the message to the message queue, that will be later used by the linker.

        Args:
            teammate_number: The number representing the player to which we want to sen the message
            message: The message to send
        """
        self.messagesToTeammates.put(TeammatePayload(teammate_number, message))

    @abstractmethod
    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        """
        Main function for collaboration between teammates.
        Reacts when a collaboration message is received from the teammate represented by the given number

        Args:
            teammate_number: The number representing the teammate sending the message
            message: The message sent by the teammate

        Returns:
            The new move descriptor (if any) that results from the teammate's message
        """
        pass

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
        Returns the move. The move returned must return a correct move for the game (see self._isMoveAllowed)

        Args:
            game_state:
                The game state to react to. This game state must not be modified in place, in order to
                maintain a stable local copy of the game state.
        """
        pass

    @abstractmethod
    def _getGameStateAPI(self, game: Game):
        """
        Generate the API of the game state, which will be used by this controller to make decisions.

        Args:
            game: The game that will be used by the API to get information

        Returns: A new API to interact with
        """
        return GameState(game)

    @abstractmethod
    def _isMoveAllowed(self, move) -> bool:
        """

        Args:
            move: The move to determine if allowed or not

        Returns: True if the move is allowed. False otherwise
        """
        pass

