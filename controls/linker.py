from abc import ABCMeta, abstractmethod
from queue import Empty

import pygame
from multiprocess.connection import PipeConnection

from controls.controller import Controller
from controls.event import Event
from controls.events.special import SpecialEvent

MAX_FPS = 30


class Linker(metaclass=ABCMeta):
    def __init__(self, controller: Controller):
        self._unitAlive = True
        self.controller = controller
        self._connected = True
        self.mainPipe = None
        self.gameInfoPipe = None

    def setMainPipe(self, main_pipe: PipeConnection):
        """
        Sets the main pipe of this linker

        Args:
            main_pipe: The pipe connection to the game
        """
        self.mainPipe = main_pipe

    def setGameInfoPipe(self, game_info_pipe: PipeConnection):
        """
        Sets the game info pipe of this linker

        Args:
            game_info_pipe: The pipe connection to the game information
        """
        self.gameInfoPipe = game_info_pipe

    @property
    @abstractmethod
    def typeOfEventFromGame(self):
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

    def close(self):
        """
        Closes this linker so that the run loop ends.

        Args:
            pipe_conn:

        Returns:

        """
        self._connected = False
        self.mainPipe.close()
        self.gameInfoPipe.close()

    def run(self):
        """
        Runs the logical loop of this linker, looking for actions coming from the controller and updating
        the controller's local copy of the game state. The loop runs with a maximum of MAX_FPS iteration/s

        Args:
            pipe_conn: The pipe connection used to communicate game events with the game
            game_info_pipe_conn: The pipe connection used to communicate game info with the game
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
            events.append(self.mainPipe.recv())
        if len(events) is not None:
            for event in events:
                if not isinstance(event, self.typeOfEventFromGame):
                    raise TypeError('The linker received a \'%s\' event and waited a \'%s\' event'
                                    % (str(type(event)), str(self.typeOfEventFromGame)))
            self.controller.reactToEvents(events)

    def checkGameInfo(self):
        """
        Check if there is an update on the game information.

        Args:
            pipe_conn: The connection through which the game pass the information
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

    def fetchControllerMoveDescriptor(self):
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

    def _routine(self):
        """
        Defines what happens in the loop of the linker.
        Can optionally be overridden.
        """
        if self._unitAlive:
            self.sendControllerActionsIfNeeded()
        self.checkGameInfo()
        self.handleNewGameStateChangeIfNeeded()

    def _sendActionToGame(self, move_descriptor):
        """
        Sends the given move descriptor to the game through the given pipe
        Args:
            move_descriptor: The action to send to the game
        """
        if move_descriptor is not None and self.isMoveDescriptorAllowed(move_descriptor):
            self.mainPipe.send(move_descriptor)


