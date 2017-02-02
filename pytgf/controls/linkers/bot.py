"""
File containing the definition of a Bot Linker, linking the game with a bot controller
"""

from abc import ABCMeta
from queue import Empty
from queue import Queue
from typing import Dict

from multiprocess.connection import PipeConnection

from pytgf.controls.controllers.bot import Bot, TeammatePayload, TeammateMessage
from pytgf.controls.events.bot import BotEvent
from pytgf.controls.linkers.linker import Linker

__author__ = 'Anthony Rouneau'


class BotLinker(Linker, metaclass=ABCMeta):
    """
    Defines a Linker that is meant to be the medium between the Game and a Bot Controller
    """
    def __init__(self, controller: Bot):
        """
        Instantiates this linker with the given controller

        Args:
            controller: The bot controller with which this linker will communicate
        """
        super().__init__(controller)
        self._collaborationPipes = {}  # type: Dict[int, PipeConnection]

    # -------------------- PUBLIC METHODS -------------------- #

    @property
    def typeOfEventFromGame(self) -> type:
        """
        Returns: The type of the event that will be received from the game: BotEvent
        """
        return BotEvent

    def reactToTeammateMessage(self, teammate_number: int, message: TeammateMessage) -> None:
        """
        Checks what returns the controller following the message of its teammate.
        If the return is an allowed move, put it into the move queue

        Args:
            teammate_number: The number representing the teammate that sent the message
            message: The message sent by the teammate
        """
        res = self.controller.selectMoveFollowingTeammateMessage(teammate_number, message)
        if self.isMoveDescriptorAllowed(res):
            self.controller.moves.put(res)

    def addCollaborationPipe(self, player_number: int, pipe: PipeConnection) -> None:
        """
        Adds a communication pipe so that this bot can send collaboration messages to its teammates.

        Args:
            player_number: The number representing the teammate
            pipe: The pipe that will be used to send and receive message toward and from the teammates of this Bot.
        """
        self._collaborationPipes[player_number] = pipe

    # -------------------- PROTECTED METHODS -------------------- #

    def _routine(self) -> None:
        """
        Runs every tick of this linker, update the game state of the controller, and send event to the game or to the
        controller if needed. (Sends also teammate messages)
        """
        self._reactToTeammatesIfNeeded()
        self._sendToTeammatesIfNeeded()
        super()._routine()

    def _reactToTeammatesIfNeeded(self) -> None:
        """
        Checks if there is messages waiting from the teammates. If there is, react to their message
        """
        for teammate_number, teammate_pipe in self._collaborationPipes.items():
            if teammate_pipe.poll():
                message = teammate_pipe.recv()  # type: TeammateMessage
                self.reactToTeammateMessage(teammate_number, message)

    def _sendToTeammatesIfNeeded(self) -> None:
        """
        Sends the messages of the controller of this linker that await to be sent to teammates
        """
        try:
            while True:
                qu = self.controller.messagesToTeammates  # type: Queue
                message = qu.get_nowait()  # type: TeammatePayload
                if message.teammateNumber in self._collaborationPipes:
                    self._collaborationPipes[message.teammateNumber].send(message.message)
        except Empty:
            pass

