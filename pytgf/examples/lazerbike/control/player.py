"""
File containing the basic player for the lazerbike game
"""

from abc import ABCMeta
from typing import List

from ..gamedata import GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN
from ..rules import LazerBikeAPI, LazerBikeCore
from ....characters.moves import MoveDescriptor
from ....controls.controllers import Controller, Bot


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
        self._playersMove = []

    @property
    def possibleMoves(self) -> List[MoveDescriptor]:
        return [GO_RIGHT, GO_DOWN, GO_LEFT, GO_UP]

    def _getGameStateAPI(self, game: LazerBikeCore) -> LazerBikeAPI:
        """
        Get the API specific to this game

        Args:
            game: The game that the API will use

        Returns: The specific API
        """
        return LazerBikeAPI(game)

    def _isMoveInteresting(self, player_number: int, new_move_event: MoveDescriptor) -> bool:
        """

        Args:
            player_number: The player that performs the given move
            new_move_event: The descriptor of the performed move

        Returns: True if the given move must trigger a new move selection from this controller
        """
        self._playersMove.append(player_number)
        if len(self._playersMove) >= len(self.gameState.getAlivePlayersNumbers()):
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
        return move in self.possibleMoves
