"""
File containing the basic player for the lazerbike game
"""

from abc import ABCMeta

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.controllers import Controller, Bot
from pytgf.examples.lazerbike.control import LazerBikeGameState, GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN
from pytgf.game import Game


class LazerBikePlayer(Controller, metaclass=ABCMeta):
    """
    Defines the basic player for the lazerbike game
    """
    pass


class LazerBikeBotPlayer(LazerBikePlayer, Bot, metaclass=ABCMeta):
    """
    Defines the basic bot player for the lazerbike game
    """
    def __init__(self, player_number):
        """
        Instantiates an abstract bot controller that is meant to play the lazerbike game

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self.availableMoves = [GO_DOWN, GO_UP, GO_RIGHT, GO_LEFT]
        self._playersMove = []

    def _getGameStateAPI(self, game: Game) -> LazerBikeGameState:
        """
        Get the API specific to this game

        Args:
            game: The game that the API will use

        Returns: The specific API
        """
        return LazerBikeGameState(game)

    def _isMoveInteresting(self, player_number: int, new_move_event: MoveDescriptor) -> bool:
        """

        Args:
            player_number: The player that performs the given move
            new_move_event: The descriptor of the performed move

        Returns: True if the given move must trigger a new move selection from this controller
        """
        self._playersMove.append(player_number)
        if len(self._playersMove) >= self.gameState.getNumberOfAlivePlayers():
            self._playersMove = []
            return True
        else:
            return False

    def _isMoveAllowed(self, move: MoveDescriptor) -> bool:
        """
        Args:
            move: The descriptor of the wanted move

        Returns: True if the given move descriptor is allowed by the game
        """
        return move in (GO_RIGHT, GO_DOWN, GO_LEFT, GO_UP)
