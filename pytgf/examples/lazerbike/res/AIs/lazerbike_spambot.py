"""
File containing the definition of a bot controller taking random decisions
"""

import random
from threading import Thread

import pygame.time

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.controllers import TeammateMessage
from pytgf.examples.lazerbike.controllers.player import LazerBikeBotPlayer
from pytgf.game.api import API

SPAM_RATE=100


def run(bot: "SpamBot"):
    timer = clock = pygame.time.Clock()
    moves = bot.possibleMoves + ["1", "2", "3", "4"]
    while True:
        action = random.choice(moves)
        bot.moves.put(action)
        timer.tick(SPAM_RATE)


class SpamBot(LazerBikeBotPlayer):
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
        self.__thread = Thread(target=lambda: run(self))
        self.__first = True
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
        if self.__first:
            self.__first = False
            self.__thread.start()

    def _isMoveInteresting(self, player_number: int, new_move_event: MoveDescriptor):
        return True

    def _isMoveAllowed(self, move: MoveDescriptor):
        return True