"""
File containing the definition of an abstract ControllerWrapper, linking the game with a Controller
"""

from abc import ABCMeta, abstractmethod
from queue import Empty

import pygame
from typing import Any

from pytgf.controls.events.multiple import MultipleEvents

try:
    from multiprocess.connection import PipeConnection
except ImportError:
    PipeConnection = object

from pytgf.controls.controllers.controller import Controller
from pytgf.controls.events.event import Event
from pytgf.controls.events.special import SpecialEvent

__author__ = 'Anthony Rouneau'

MAX_FPS = 30


class ControllerWrapper(metaclass=ABCMeta):
    """
    Defines a ControllerWrapper that will be the medium between the Game and a controller.
    """

    def __init__(self, controller: Controller):
        """
        Instantiates this ControllerWrapper

        Args:
            controller: The controller with which the ControllerWrapper will communicate
        """
        self._unitAlive = True
        self.controller = controller
        self._connected = True
        self.mainPipe = None
        self.gameInfoPipe = None

    # -------------------- PUBLIC METHODS -------------------- #

    def setMainPipe(self, main_pipe: PipeConnection) -> None:
        """
        Sets the main pipe of this linker

        Args:
            main_pipe: The pipe connection to the game
        """
        self.mainPipe = main_pipe

    def setGameInfoPipe(self, game_info_pipe: PipeConnection) -> None:
        """
        Sets the game info pipe of this linker

        Args:
            game_info_pipe: The pipe connection to the game information
        """
        self.gameInfoPipe = game_info_pipe

    @property
    @abstractmethod
    def typeOfEventFromGame(self) -> type:
        """
        Returns: The type of event this linker waits from the game
        """
        pass

    @abstractmethod
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        """
        Args:
            move_descriptor: The descriptor of the move that will be analysed by this method

        Returns: True if the given move description is allowed by the game.
        """
        pass

    def close(self) -> None:
        """
        Closes this linker so that the run loop ends.
        """
        self._connected = False
        self.mainPipe.close()
        self.gameInfoPipe.close()

    def run(self) -> None:
        """
        Runs the logical loop of this linker, looking for actions coming from the controller and updating
        the controller's local copy of the game state. The loop runs with a maximum of MAX_FPS iteration/s
        """
        clock = pygame.time.Clock()
        while self._connected:
            try:
                self._routine()
            except (BrokenPipeError, EOFError, OSError):
                self.close()
            finally:
                clock.tick(MAX_FPS)

    def handleNewGameStateChangeIfNeeded(self) -> None:
        """
        Polls into the given pipe connection if there is a new change in the game state that must be replicated into the
        controller's local copy. If there is, sends it to the controller.
        """
        events = []
        while self.mainPipe.poll():
            event = self.mainPipe.recv()
            if isinstance(event, MultipleEvents):
                events.extend(event.events)
            else:
                events.append(event)
        if len(events) is not None:
            for event in events:
                if not isinstance(event, self.typeOfEventFromGame):
                    raise TypeError('The linker received a \'%s\' event and waited a \'%s\' event'
                                    % (str(type(event)), str(self.typeOfEventFromGame)))
            self.controller.reactToEvents(events)

    def checkGameInfo(self) -> None:
        """
        Check if there is an update on the game information.
        """
        event = None
        while self.gameInfoPipe.poll():
            event = self.gameInfoPipe.recv()  # type: Event
        if isinstance(event, SpecialEvent):
            if event.flag == SpecialEvent.END:
                self.close()
            elif event.flag == SpecialEvent.UNIT_KILLED:
                self._unitAlive = False
            elif event.flag == SpecialEvent.RESURRECT_UNIT:
                self._unitAlive = True

    def sendControllerActionsIfNeeded(self) -> None:
        """
        Looks in the controller if a move is waiting to be handled. If there is, checks if the move is correct for the
        game using the "isMoveDescriptorAllowed" method and sends it to the game using the pipe connection if
        it is allowed.
        """
        move_descriptor = self.fetchControllerMoveDescriptor()
        self._sendActionToGame(move_descriptor)

    def fetchControllerMoveDescriptor(self) -> Any:
        """
        Returns: The action descriptor given by the controller or None if there is no action pending in the controller
        """
        action = None
        try:
            while True:
                action = self.controller.moves.get_nowait()
        except Empty:
            pass
        return action

    # -------------------- PROTECTED METHODS -------------------- #

    def _routine(self) -> None:
        """
        Defines what happens in the loop of the linker. (Sends and receive message to the game and the controller)
        Can optionally be overridden.
        """
        if self._unitAlive:
            self.sendControllerActionsIfNeeded()
        self.checkGameInfo()
        self.handleNewGameStateChangeIfNeeded()

    def _sendActionToGame(self, move_descriptor: Any) -> None:
        """
        Sends the given move descriptor to the game through the given pipe
        Args:
            move_descriptor: The action to send to the game
        """
        if move_descriptor is not None and self.isMoveDescriptorAllowed(move_descriptor):
            self.mainPipe.send(move_descriptor)


