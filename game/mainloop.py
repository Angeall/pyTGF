import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty

import pygame
from pygame.constants import DOUBLEBUF, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT

from board.tile import Tile
from characters.controller import Controller
from characters.controllers.bot import Bot
from characters.controllers.human import Human
from characters.moves.move import IllegalMove, ImpossibleMove
from characters.moves.path import Path
from characters.units.moving_unit import MovingUnit
from characters.units.unit import Unit
from game.game import Game, UnfeasibleMoveException
from game.gamestate import GameState
from utils.unit import resize_unit

CONTINUE = 0
PAUSE = 1
END = 2
FINISH = 3
MAX_FPS = 30


class MainLoop:
    def __init__(self, game: Game):
        self.game = game
        self.game.addCustomMoveFunc = self._addCustomMove
        self._screen = None
        self._state = CONTINUE  # The game must go on at start
        # self._controllers -> keys: controllers; values: Units
        self.controllers = {}
        # self._controllersMoves -> keys: controllers; values: tuples (current_move, pending_moves)
        self._controllersMoves = {}
        # self._movesEvent -> keys: moves; values: events (that triggered its key move)
        self._movesEvent = {}
        # self._otherMoves -> keys: units; values: queue
        self._otherMoves = {}
        self.executor = None

    def run(self, max_fps: int=MAX_FPS) -> tuple:
        """
        Launch the game and its logical loop

        Args:
            max_fps: The maximum frame per seconds of the game

        Returns:
            a tuple containing all the winning players, or an empty tuple in case of draw,
            or None if the game was closed by the user
        """
        pygame.init()
        clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.game.board.size, DOUBLEBUF)
        for controller in self.controllers:
            if isinstance(controller, Bot):
                controller.gameState = GameState(self.game.copy())
        while self._state != END:
            clock.tick(max_fps)
            self._handleInputs()
            if self._state == CONTINUE:
                self._handleControllersEvents()
                self._handlePendingMoves()
                self._refreshScreen()
                self._state = self._checkGameState()
            elif self._state == FINISH:
                return None
        return self.game.winningPlayers

    def addUnit(self, unit: MovingUnit, controller: Controller, tile_id, initial_action: Path = None, team: int = -1) -> None:
        """
        Adds a unit to the game, located on the tile corresponding
        to the the given tile id and controlled by the given controller

        Args:
            unit: The unit to add to the game
            controller: The controller of that unit
            tile_id: The identifier of the tile it will be placed on
            initial_action: The initial action of the unit
            team: The number of the team this player is in (-1 = no team)
        """
        self.controllers[controller] = unit
        self.game.addUnit(unit, team, tile_id)
        self._controllersMoves[controller] = (None, Queue())
        tile = self.game.board.getTileById(tile_id)
        tile.addOccupant(unit)
        resize_unit(unit, tile)
        unit.moveTo(tile.graphics.center)
        if initial_action is not None:
            self._handleControllerEvent(controller, initial_action)

    def _getUnitFromController(self, controller: Controller) -> MovingUnit:
        """
        Args:
            controller: The controller that controls the wanted unit

        Returns: The unit controlled by the given controller
        """
        return self.controllers[controller]

    def _refreshScreen(self) -> None:
        """
        Update the visual state of the game
        """
        self.game.board.draw(self._screen)
        for unit in self.controllers.values():
            unit.draw(self._screen)
        pygame.display.flip()

    def _handleInputs(self) -> None:
        """
        Handles all the user input (mouse and keyboard)
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                self._state = FINISH
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    if self._state == CONTINUE:
                        self.pause()
                    elif self._state == PAUSE:
                        self.resume()
                else:
                    self._dispatchInputToHumanControllers(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self._dispatchMouseEventToHumanControllers(event.pos)
            elif event.type == MOUSEBUTTONUP:
                self._dispatchMouseEventToHumanControllers(None, click_up=True)

    def _addMove(self, controller: Controller, move: Path) -> None:
        """
        Adds a move (cancelling the pending moves)

        Args:
            controller: The controller for which add a move
            move: The move to add for the given controller
        """
        if self._controllersMoves[controller][0] is not None:
            self._cancelCurrentMoves(controller)
        fifo = self._controllersMoves[controller][1]  # type: Queue
        fifo.put(move)
        # print((self._controllersMoves[controller][0], fifo))

    def _addCustomMove(self, unit: Unit, move: Path) -> None:
        """
        Adds a move that is NOT PERFORMED BY A CONTROLLER

        Args:
            unit: The unit that will be moved
            move: The move that will be performed
        """
        if unit not in self._otherMoves or self._otherMoves[unit] is None:
            self._otherMoves[unit] = move

    def _cancelCurrentMoves(self, controller) -> None:
        """
        Cancel the current movement if there is one and remove all the other pending movements.

        Args:
            controller: The controller for which cancel the movements
        """
        move_tuple = self._controllersMoves[controller]  # type: tuple
        fifo = move_tuple[1]  # type: Queue
        last_move = move_tuple[0]  # type: Path
        new_fifo = Queue()
        if last_move is not None:
            last_move.stop()
        while True:
            try:
                move = fifo.get_nowait()
                del self._movesEvent[move]
            except Empty:
                break
        self._controllersMoves[controller] = (last_move, new_fifo)

    def _dispatchInputToHumanControllers(self, input_key) -> None:
        """
        Handles keyboard events and send them to Human Controllers to trigger actions if needed

        Args:
            input_key: The key pressed on the keyboard
        """
        for controller in self.controllers.keys():  # type: Human
            if isinstance(controller, Human):
                self._sendInputToHumanController(controller, input_key)

    def _dispatchMouseEventToHumanControllers(self, pixel, click_up=False) -> None:
        """
        Handles mouse events and send them to Human Controllers to trigger actions if needed

        Args:
            pixel: The pixel clicked
            click_up: True if the button was released, False if the button was pressed
        """
        tile = None
        if pixel is not None:
            tile = self.game.board.getTileByPixel(pixel)
        self._previouslyClickedTile = tile
        mouse_state = pygame.mouse.get_pressed()
        for controller in self.controllers:  # type: Human
            if issubclass(type(controller), Human):
                self._sendMouseEventToHumanController(controller, tile, mouse_state, click_up)

    def _handleControllersEvents(self) -> None:
        """
        Gets event from the controls and dispatch them to the right method
        """
        for controller in self.controllers:
            try:
                move = controller.moves.get_nowait()
                self._handleControllerEvent(controller, move)
            except Empty:
                pass

    def _handlePendingMoves(self) -> None:
        """
        Get the next move to be performed and perform its next step
        """
        moved_units = []
        for controller in self.controllers:
            unit = self.controllers[controller]
            current_move = self._getNextMoveForControllerIfNeeded(controller)
            moved = self._handleMoveForUnit(unit, current_move, controller)
            if moved:
                moved_units.append(unit)

        for unit in self._otherMoves:  # type: Unit
            if unit not in moved_units:  # Two moves on the same unit cannot be performed at the same time...
                unit_controller = None
                for controller in self.controllers:
                    if self.controllers[controller] is unit:
                        unit_controller = controller
                if unit_controller is not None:
                    if self._otherMoves[unit] is not None:
                        self._handleMoveForUnit(unit, self._otherMoves[unit], unit_controller)
                        if self._otherMoves[unit].finished():
                            self._otherMoves[unit] = None

    def _handleMoveForUnit(self, unit: Unit, current_move: Path, controller: Controller):
        """
        Perform the next step of the given move on the given unit

        Args:
            unit: The unit that performs the move
            current_move: The current move to perform
            controller: The controller that controls this move (can be None if the move is not linked with a controller)
        """
        if unit.isAlive():
            if current_move is not None:
                try:
                    tile_id = current_move.performNextMove()
                    if tile_id is not None:  # A new tile has been reached by the movement
                        self.game.updateGameState(self.controllers[controller], tile_id)
                        self._informBotOnPerformedMove(controller.playerNumber, current_move)
                    return True
                except IllegalMove:
                    unit.kill()
                    self._cancelCurrentMoves(controller)
                except ImpossibleMove:
                    self._cancelCurrentMoves(controller)
                finally:
                    return False
        else:
            if current_move is not None:
                current_move.stop(cancel_post_action=True)
                return False

    def _getNextMoveForControllerIfNeeded(self, controller) -> Path:
        """
        Checks if a move is available for the given controller, and if so, returns it

        Args:
            controller: The given controller

        Returns: The next move if it is available, and None otherwise
        """
        moves = self._controllersMoves[controller]
        current_move = moves[0]  # type: Path
        if current_move is None or current_move.finished():
            try:
                if current_move is not None:
                    del self._movesEvent[current_move]
                move = moves[1].get_nowait()  # type: Path
                self._controllersMoves[controller] = (move, moves[1])
                current_move = move
            except Empty:
                self._controllersMoves[controller] = (None, moves[1])
                current_move = None
        return current_move

    def _checkGameState(self) -> int:
        """
        Checks if the game is finished

        Returns: 0 = CONTINUE; 2 = END
        """
        if self.game.isFinished():
            self.winningPlayers = self.game.winningPlayers
            return END
        return CONTINUE

    def pause(self) -> None:
        """
        Change the state of the game to "PAUSE"
        """
        self._state = PAUSE

    def resume(self) -> None:
        """
        Resume the game
        """
        self._state = CONTINUE

    def _handleControllerEvent(self, controller: Controller, event) -> None:
        """
        The goal of this method is to grab controls from the given controller and handle them in the game

        Args:
            controller: The controller to handle
            event: The event sent by the controller
        """
        try:
            move = self.game.createMoveForEvent(self.controllers[controller], event)
            self._movesEvent[move] = event
            self._addMove(controller, move)
        except UnfeasibleMoveException:
            pass

    def _informBotOnPerformedMove(self, moved_unit_number: int, move: Path):
        if self.executor is None:
            self.executor = ThreadPoolExecutor(max_workers=len(self.controllers))
        for controller in self.controllers:
            if isinstance(controller, Bot):
                try:
                    event = self._movesEvent[move]
                    controller.moveGameState(moved_unit_number, event)
                except Exception:
                    traceback.print_exc()

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple,
                                         click_up: bool) -> None:
        """
        Can optionally filter the mouse events to send

        Args:
            controller: The controller to which the event must be sent
            tile: The tile that was clicked on
            mouse_state: The mouse state (To know which button of the mouse is pressed)
            click_up: True if the button was released, False if the button was pressed
        """
        if tile is not None:
            controller.reactToTileClicked(tile.identifier, mouse_state, click_up,
                                          player_tile=self.game.getTileForUnit(self.controllers[controller]).identifier)

    def _sendInputToHumanController(self, controller: Human, input_key: int) -> None:
        """
        Can optionally filter the keyboard events to send

        Args:
            controller: The controller to which the event must be sent
            input_key: The key pressed on the keyboard
        """
        controller.reactToInput(input_key,
                                player_tile=self.game.getTileForUnit(self.controllers[controller]).identifier)
