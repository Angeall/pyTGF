from abc import ABCMeta, abstractmethod
from queue import Queue, Empty

import pygame
from pygame.locals import *

from display.tile import Tile
from characters.controller import Controller
from characters.controllers.human import Human
from characters.moves.path import Path
from characters.unit import Unit
from display.board import Board


MAX_FPS = 60


class Game(metaclass=ABCMeta):

    def __init__(self, board: Board):
        self.board = board
        self._screen = None
        self._previouslyClickedTile = None
        # self.units -> keys: units; values: tile_ids
        self.units = {}  # type: dict
        # self._controllers -> keys: controllers; values: units
        self._controllers = {}
        # self._controllersMoves -> keys: controllers; values: moves
        self._controllersMoves = {}

    def run(self, max_fps: int=MAX_FPS):
        clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.board.size, DOUBLEBUF + HWSURFACE)
        while True:
            self._handleInputs()
            self._handleControllersEvents()
            self._handlePendingMoves()
            self._refreshScreen()
            clock.tick(max_fps)

    def _refreshScreen(self):
        self.board.draw(self._screen)
        pygame.display.flip()

    def _handleInputs(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return
                else:
                    self._dispatchInputToHumanControllers(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self._dispatchMouseEventToHumanControllers(event.pos)
            elif event.type == MOUSEBUTTONUP:
                self._dispatchMouseEventToHumanControllers(None, click_up=True)

    def addMove(self, controller: Controller, move: Path) -> None:
        """
        Adds a move (cancelling the pending moves)
        Args:
            controller: The controller for which add a move
            move: The move to add for the given controller
        """
        self._cancelCurrentMoves(controller)
        fifo = self._controllersMoves[controller]  # type: Queue
        fifo.put(move)

    def _cancelCurrentMoves(self, controller) -> None:
        """
        Cancel the current movement if there is one and remove all the other pending movements.
        Args:
            controller: The controller for which cancel the movements
        """
        try:
            fifo = self._controllersMoves[controller]  # type: Queue
            last_move = fifo.get()  # type: Path
            fifo.
            last_move.cancel()
            del fifo
            new_fifo = Queue()
            new_fifo.put(last_move)
            self._controllersMoves[controller] = new_fifo
        except Empty:
            pass

    def addUnit(self, unit: Unit, controller: Controller, tile_id: ...) -> None:
        self._controllers[controller] = unit
        self._controllersMoves[controller] = Queue()
        self.units[unit] = tile_id

    @abstractmethod
    def _sendInputToHumanController(self, controller: Human, input_key: int):
        pass

    def _dispatchInputToHumanControllers(self, input_key):
        for controller in self._controllers.keys():  # type: Human
            if type(controller) == Human:
                self._sendInputToHumanController(controller, input_key)

    @abstractmethod
    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple, click_up: bool):
        pass

    def _dispatchMouseEventToHumanControllers(self, pixel, click_up=False):
        tile = None
        if pixel is not None:
            tile = self.board.getTileByPixel(pixel)
        self._previouslyClickedTile = tile
        mouse_state = pygame.mouse.get_pressed()
        for controller in self._controllers.keys():  # type: Human
            if type(controller) == Human:
                self._sendMouseEventToHumanController(controller, tile, mouse_state, click_up)

    def _handleControllersEvents(self):
        for controller in self._controllers.keys():
            move = controller.moves.get()
            self._handleControllerEvent(controller, move)

    @abstractmethod
    def _handleControllerEvent(self, controller: Controller, event: ...) -> None:
        """
        The goal of this method is to grab controls from the given controller and handle them in the game
        Args:
            controller: The controller to handle
            event: The event sent by the controller
        """
        pass

    def _handlePendingMoves(self):
        # TODO Get the current move (without removing it from the queue) for each controller and perform the next step of it
        pass
