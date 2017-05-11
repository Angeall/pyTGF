"""
File containing the definition of a bot controller taking random decisions
"""

import random

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.controllers import TeammateMessage
from pytgf.examples.lazerbike.control.player import LazerBikeBotPlayer
from pytgf.examples.lazerbike.rules import LazerBikeAPI


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

    def _selectNewMove(self, game_state: LazerBikeAPI) -> MoveDescriptor:
        """
        Selects a new random move following a new game state

        Args:
            game_state: The new game state to react to

        Returns:

        """
        move = random.choice(self.possibleMoves)
        succeeded, _ = game_state.simulateMove(self.playerNumber, move)
        suicidal_moves = []
        suicidal = game_state.isMoveSuicidal(self.playerNumber, move)
        while not succeeded or (suicidal and len(suicidal_moves) < 3):
            move = random.choice(self.possibleMoves)
            succeeded, _ = game_state.simulateMove(self.playerNumber, move)
            suicidal = game_state.isMoveSuicidal(self.playerNumber, move)
            if succeeded and suicidal and move not in suicidal_moves:
                suicidal_moves.append(move)
        return move
