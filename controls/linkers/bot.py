from abc import ABCMeta
from queue import Empty
from queue import Queue
from typing import Dict

from multiprocess.connection import PipeConnection

from controls.controllers.bot import Bot
from controls.controllers.bot import TeammatePayload
from controls.events.bot import BotEvent
from controls.linker import Linker


class BotLinker(Linker, metaclass=ABCMeta):

    def __init__(self, controller: Bot):
        super().__init__(controller)
        self._collaborationPipes = {}  # type: Dict[int, PipeConnection]

    def addCollaborationPipe(self, player_number: int, pipe: PipeConnection):
        """
        Adds a communication pipe so that this bot can send collaboration messages to its teammates.

        Args:
            player_number: The number representing the teammate
            pipe: The pipe that will be used to send and receive message toward and from the teammates of this Bot.
        """
        self._collaborationPipes[player_number] = pipe

    def _routine(self):
        self._reactToTeammatesIfNeeded()
        self._sendToTeammatesIfNeeded()
        super()._routine()

    def _reactToTeammatesIfNeeded(self):
        """
        Checks if there is messages waiting from the teammates. If there is, react to their message
        """
        for teammate_number, teammate_pipe in self._collaborationPipes.items():
            if teammate_pipe.poll():
                message = teammate_pipe.recv()
                self.reactToTeammateMessage(teammate_number, message)

    def reactToTeammateMessage(self, teammate_number: int, message):
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

    def _sendToTeammatesIfNeeded(self):
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

    @property
    def typeOfEventFromGame(self):
        return BotEvent
