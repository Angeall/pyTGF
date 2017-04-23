"""
File containing the definition of a bot controller taking random decisions
"""

import random

from ...control.player import LazerBikeBotPlayer
from .....characters.moves import MoveDescriptor
from .....controls.controllers import TeammateMessage
from .....game.api import API


class RandomBot(LazerBikeBotPlayer):
    """
    Defines a bot controller that takes random decisions
    """

    def __init__(self, player_number: int):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self._playersMove = []

    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message: TeammateMessage) -> None:
        """
        Does nothing special if it receives a message from a teammate

        Args:
            teammate_number: The number representing the teammate sending the message
            message: The message sent by the teammate
        """
        pass

    def _selectNewMove(self, game_state: API) -> MoveDescriptor:
        """
        Selects a new random move following a new game state

        Args:
            game_state: The new game state to react to

        Returns:

        """
        return random.choice(self.availableMoves)
