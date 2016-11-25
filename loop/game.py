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
        # self._units -> keys: Units; values: tile_ids
        self._units = {}  # type: dict
        # self._controllers -> keys: controllers; values: _units
        self._controllers = {}
        # self._controllersMoves -> keys: controllers; values: tuples (current_move, pending_moves)
        self._controllersMoves = {}

    def run(self, max_fps: int=MAX_FPS):
        pygame.init()
        clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.board.size, DOUBLEBUF + HWSURFACE)
        while True:
            if not self._handleInputs():
                return
            self._handleControllersEvents()
            self._handlePendingMoves()
            self._refreshScreen()
            clock.tick(max_fps)

    def _refreshScreen(self):
        self.board.draw(self._screen)
        pygame.display.flip()

    def _handleInputs(self) -> bool:
        """
        Handles all the user input (mouse and keyboard)
        Returns: True if the game must continue, False otherwise
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return False
                else:
                    self._dispatchInputToHumanControllers(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self._dispatchMouseEventToHumanControllers(event.pos)
            elif event.type == MOUSEBUTTONUP:
                self._dispatchMouseEventToHumanControllers(None, click_up=True)
        return True

    def _addMove(self, controller: Controller, move: Path) -> None:
        """
        Adds a move (cancelling the pending moves)
        Args:
            controller: The controller for which add a move
            move: The move to add for the given controller
        """
        self._cancelCurrentMoves(controller)
        fifo = self._controllersMoves[controller][1]  # type: Queue
        fifo.put(move)

    def _getUnitFromController(self, controller: Controller) -> Unit:
        return self._controllers[controller]

    def _getTileForUnit(self, unit: Unit) -> Tile:
        return self.board.getTileById(self._units[unit])

    def _cancelCurrentMoves(self, controller) -> None:
        """
        Cancel the current movement if there is one and remove all the other pending movements.
        Args:
            controller: The controller for which cancel the movements
        """
        try:
            move_tuple = self._controllersMoves[controller] # type: Queue
            fifo = move_tuple[1]
            last_move = move_tuple[0]  # type: Path
            new_fifo = Queue()
            if last_move is not None:
                last_move.cancel()
                new_fifo.put(last_move)
            del fifo
            self._controllersMoves[controller] = (last_move, new_fifo)
        except Empty:
            pass

    def addUnit(self, unit: Unit, controller: Controller, tile_id, initial_action: Path=None) -> None:
        """
        Adds a unit to the game, located on the tile corresponding
        to the the given tile id and controlled by the given controller
        Args:
            unit: The unit to add to the game
            controller: The controller of that unit
            tile_id: The identifier of the tile it will be placed on
            initial_action: The initial action of the unit
        """
        self._controllers[controller] = unit
        self._controllersMoves[controller] = (None, Queue())
        self._units[unit] = tile_id
        tile = self.board.getTileById(tile_id)
        tile.addOccupant(unit)
        unit.moveTo(tile.center)
        if initial_action is not None:
            self._handleControllerEvent(controller, initial_action)

    @abstractmethod
    def _sendInputToHumanController(self, controller: Human, input_key: int):
        pass

    def _dispatchInputToHumanControllers(self, input_key):
        for controller in self._controllers.keys():  # type: Human
            if isinstance(controller, Human):
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
            try:
                move = controller.moves.get_nowait()
                self._handleControllerEvent(controller, move)
            except Empty:
                pass

    @abstractmethod
    def _handleControllerEvent(self, controller: Controller, event) -> None:
        """
        The goal of this method is to grab controls from the given controller and handle them in the game
        Args:
            controller: The controller to handle
            event: The event sent by the controller
        """
        pass

    def _handlePendingMoves(self) -> None:
        """
        Get the next move to be performed and perform its next step
        """
        for controller in self._controllers.keys():
            moves = self._controllersMoves[controller]
            current_move = moves[0]  # type: Path
            if current_move is None or current_move.cancelled or current_move.completed:
                try:
                    move = moves[1].get_nowait()  # type: Path
                    self._controllersMoves[controller] = (move, moves[1])
                    current_move = move
                except Empty:
                    self._controllersMoves[controller] = (None, moves[1])
                    current_move = None
            if current_move is not None:
                tile_id = current_move.performNextMove()
                if tile_id is not None:  # A new tile has been reached by the movement
                    unit = self._controllers[controller]
                    old_tile_id = self._units[unit]
                    self._units[unit] = tile_id
                    self.board.getTileById(old_tile_id).removeOccupant(unit)
                    self.board.getTileById(tile_id).addOccupant(unit)
                if current_move.cancelled or current_move.completed:
                    pass  # TODO check for collisions
