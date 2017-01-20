import traceback
from abc import ABCMeta, abstractmethod
from queue import Empty, Queue
import time

import pygame
from multiprocess.connection import PipeConnection
from pathos.pools import ThreadPool

from controls.controller import Controller
from controls.event import Event
from controls.events.special import SpecialEvent

MAX_FPS = 30


class Linker(metaclass=ABCMeta):
    def __init__(self, controller: Controller):
        self._unitAlive = True
        self.controller = controller
        self._connected = True
        self.executor = ThreadPool(1)

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

    def close(self, pipe_conn: PipeConnection):
        """
        Closes this linker so that the run loop ends.

        Args:
            pipe_conn:

        Returns:

        """
        self._connected = False
        pipe_conn.close()

    def run(self, pipe_conn: PipeConnection, game_info_pipe_conn: PipeConnection):
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
                if self._unitAlive:
                    self.sendControllerActionsIfNeeded(pipe_conn)
                self.checkGameInfo(game_info_pipe_conn)
                self.handleNewGameStateChangeIfNeeded(pipe_conn)
            except BrokenPipeError:
                traceback.print_exc()
                self.close(pipe_conn)
            except EOFError:
                traceback.print_exc()
                self.close(pipe_conn)
            except:
                traceback.print_exc()
            finally:
                clock.tick(MAX_FPS)

    def handleNewGameStateChangeIfNeeded(self, pipe_conn: PipeConnection) -> None:
        """
        Polls into the given pipe connection if there is a new change in the game state that must be replicated into the
        controller's local copy. If there is, sends it to the controller.

        Args:
            pipe_conn: The pipe connection to the game
        """
        events = []
        while pipe_conn.poll():
            events.append(pipe_conn.recv())
        if len(events) is not None:
            for event in events:
                if not isinstance(event, self.typeOfEventFromGame):
                    raise TypeError('The linker received a \'%s\' event and waited a \'%s\' event'
                                    % (str(type(event)), str(self.typeOfEventFromGame)))
            # self.executor.pipe(self.controller.reactToEvent, event)
            self.controller.reactToEvents(events)

    def checkGameInfo(self, pipe_conn: PipeConnection):
        event = None
        while pipe_conn.poll():
            event = pipe_conn.recv()  # type: Event
        if isinstance(event, SpecialEvent):
            if event.flag == SpecialEvent.END:
                self.close(pipe_conn)
            elif event.flag == SpecialEvent.UNIT_KILLED:
                self._unitAlive = False
            elif event.flag == SpecialEvent.RESURRECT_UNIT:
                self._unitAlive = True

    def sendControllerActionsIfNeeded(self, pipe_conn: PipeConnection) -> None:
        """
        Look in the controller if a move is waiting to be handled. If there is, checks if the move is correct for the
        game using the "isMoveDescriptorAllowed" method and sends it to the game using the pipe connection if
        it is allowed.

        Args:
            pipe_conn: The pipe connection to the game
        """
        move_descriptor = self.fetchControllerMoveDescriptor()
        if move_descriptor is not None and self.isMoveDescriptorAllowed(move_descriptor):
            pipe_conn.send(move_descriptor)

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

