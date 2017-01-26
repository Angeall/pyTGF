import traceback
from queue import Queue, Empty
from typing import Union, Any
import time

import pygame
from multiprocess.connection import Pipe, PipeConnection
from pathos.pools import ProcessPool as Pool
from pygame.constants import DOUBLEBUF, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT

from characters.moves.move import IllegalMove, ImpossibleMove
from characters.moves.path import Path
from characters.units.moving_unit import MovingUnit
from characters.units.unit import Unit
from controls.controllers.bot import Bot
from controls.controllers.human import Human
from controls.events.bot import BotEvent
from controls.events.keyboard import KeyboardEvent
from controls.events.mouse import MouseEvent
from controls.events.special import SpecialEvent
from controls.linker import Linker
from controls.linkers.bot import BotLinker
from controls.linkers.human import HumanLinker
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
        # self.linkersConnection -> keys: Linkers; values: PipeConnections
        self.linkersConnection = {}
        self.linkersInfoConnection = {}
        self.linkersProcessConnection = {}
        # self.linkers -> keys: controllers; values: Units
        self.linkers = {}
        # self._controllersMoves -> keys: controllers; values: tuples (current_move, pending_moves)
        self._unitsMoves = {}
        # self._movesEvent -> keys: moves; values: events (that triggered its key move)
        self._movesEvent = {}
        # self._otherMoves -> keys: units; values: queue
        self._otherMoves = {}
        self._killSent = {}  # Used to maintain the fact that the kill event has been sent
        self.executor = None
        self._prepared = False

    def run(self, max_fps: int = MAX_FPS) -> Union[None, tuple]:
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
        if not self._prepared:
            self._prepareLoop()
        while self._state != END:
            self._state = self._checkGameState()
            clock.tick(max_fps)
            self._handleInputs()
            if self._state == CONTINUE:
                self._getNextMoveFromLinkerIfAvailable()
                self._handlePendingMoves()
                self._refreshScreen()
            elif self._state == FINISH:
                self.executor.terminate()
                self._prepared = False
                return None
        self.executor.terminate()
        self._prepared = False
        return self.game.winningPlayers

    def _prepareLoop(self):
        self.executor = Pool(len(self.linkers))
        try:
            self.executor.apipe(lambda: None)
        except ValueError:
            self.executor.restart()
        for linker in self.linkers:
            if issubclass(type(linker.controller), Bot):
                linker.controller.gameState = GameState(self.game.copy())
            parent_conn, child_conn = Pipe()
            parent_info_conn, child_info_conn = Pipe()
            self.linkersConnection[linker] = parent_conn
            self.linkersInfoConnection[linker] = parent_info_conn
            self.linkersProcessConnection[linker] = child_conn
            try:
                self.executor.apipe(linker.run, child_conn, child_info_conn)
            except:
                traceback.print_exc()
        time.sleep(2)
        self._prepared = True

    def addUnit(self, unit: MovingUnit, linker: Linker, tile_id, initial_action: Path = None, team: int = -1) -> None:
        """
        Adds a unit to the game, located on the tile corresponding
        to the the given tile id and controlled by the given controller

        Args:
            unit: The unit to add to the game
            linker: The linker of that unit
            tile_id: The identifier of the tile it will be placed on
            initial_action: The initial action of the unit
            team: The number of the team this player is in (-1 = no team)
        """
        self.linkers[linker] = unit
        self.game.addUnit(unit, team, tile_id)
        self._unitsMoves[unit] = (None, Queue())
        tile = self.game.board.getTileById(tile_id)
        resize_unit(unit, self.game.board)
        unit.moveTo(tile.center)
        if initial_action is not None:
            unit.currentAction = initial_action
            self._handleEvent(unit, initial_action)

    def _refreshScreen(self) -> None:
        """
        Update the visual state of the game
        """
        self.game.board.draw(self._screen)
        for unit in self.linkers.values():
            if unit.isAlive():
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

    def _addMove(self, unit: MovingUnit, move: Path) -> None:
        """
        Adds a move (cancelling the pending moves)

        Args:
            unit: The unit for which add a move
            move: The move to add for the given controller
        """
        if self._unitsMoves[unit][0] is not None:
            self._cancelCurrentMoves(unit)
        fifo = self._unitsMoves[unit][1]  # type: Queue
        fifo.put(move)

    def _addCustomMove(self, unit: Unit, move: Path, event: Any) -> None:
        """
        Adds a move that is NOT PERFORMED BY A CONTROLLER

        Args:
            unit: The unit that will be moved
            move: The move that will be performed
        """
        if unit not in self._otherMoves or self._otherMoves[unit] is None:
            self._otherMoves[unit] = move
        self._movesEvent[move] = event

    def _cancelCurrentMoves(self, unit: MovingUnit) -> None:
        """
        Cancel the current movement if there is one and remove all the other pending movements.

        Args:
            unit: The unit for which cancel the movements
        """
        move_tuple = self._unitsMoves[unit]  # type: tuple
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
        self._unitsMoves[unit] = (last_move, new_fifo)

    def _dispatchInputToHumanControllers(self, input_key) -> None:
        """
        Handles keyboard events and send them to Human Controllers to trigger actions if needed

        Args:
            input_key: The key pressed on the keyboard
        """
        for linker in self.linkers:  # type: HumanLinker
            if issubclass(type(linker), HumanLinker):
                self._getPipeConnection(linker).send(self.game.createKeyboardEvent(self._getUnitFromLinker(linker),
                                                                                   input_key))

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
        for linker in self.linkers:  # type: Linker
            if issubclass(type(linker), HumanLinker):
                tile_id = None
                if tile is not None:
                    tile_id = tile.identifier
                self._getPipeConnection(linker).send(self.game.createMouseEvent(self._getUnitFromLinker(linker),
                                                                                pixel, mouse_state, click_up, tile_id))

    def _getNextMoveFromLinkerIfAvailable(self) -> None:
        """
        Gets event from the controllers and dispatch them to the right method
        """
        for linker in self.linkersConnection:
            pipe_conn = self._getPipeConnection(linker)
            if pipe_conn.poll():
                move = pipe_conn.recv()
                self._handleEvent(self.linkers[linker], move)

    def _handlePendingMoves(self) -> None:
        """
        Get the next move to be performed and perform its next step
        """
        moved_units = []
        for linker in self.linkers:  # type: Linker
            unit = self._getUnitFromLinker(linker)
            if not unit.isAlive() and (unit not in self._killSent or not self._killSent[unit]):
                self.linkersInfoConnection[linker].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))
                self._killSent[unit] = True
            current_move = self._getNextMoveForUnitIfAvailable(unit)
            moved = self._handleMoveForUnit(unit, current_move, linker)
            if moved:
                moved_units.append(unit)

        for unit in self._otherMoves:  # type: MovingUnit
            if unit not in moved_units:  # Two moves on the same unit cannot be performed at the same time...
                unit_linker = None
                for linker in self.linkers:
                    if self._getUnitFromLinker(linker) is unit:
                        unit_linker = linker
                if unit_linker is not None:
                    if self._otherMoves[unit] is not None:
                        self._handleMoveForUnit(unit, self._otherMoves[unit], unit_linker)
                        if self._otherMoves[unit].finished():
                            self._otherMoves[unit] = None
        self.game.checkIfFinished()

    def _handleMoveForUnit(self, unit: MovingUnit, current_move: Path, linker: Linker):
        """
        Perform the next step of the given move on the given unit

        Args:
            unit: The unit that performs the move
            current_move: The current move to perform
            linker: The linker that controls this move (can be None if the move is not linked with a controller)
        """
        if unit.isAlive():
            if current_move is not None:
                try:
                    just_started, move_completed, tile_id = current_move.performNextMove()
                    if move_completed:  # A new tile has been reached by the movement
                        self.game.updateGameState(unit, tile_id)
                    elif just_started:
                        self._informBotOnPerformedMove(unit.playerNumber, current_move)
                    return True
                except IllegalMove:
                    self._killUnit(unit, linker)
                    self.game.checkIfFinished()
                    self._cancelCurrentMoves(unit)
                except ImpossibleMove:
                    self._cancelCurrentMoves(unit)
                except:
                    traceback.print_exc()
                finally:
                    return False
        else:
            if current_move is not None:
                current_move.stop(cancel_post_action=True)
                return False

    def _getNextMoveForUnitIfAvailable(self, unit: MovingUnit) -> Path:
        """
        Checks if a move is available for the given controller, and if so, returns it

        Args:
            unit: The given

        Returns: The next move if it is available, and None otherwise
        """
        moves = self._unitsMoves[unit]
        current_move = moves[0]  # type: Path
        if current_move is None or current_move.finished():
            try:
                if current_move is not None:
                    del self._movesEvent[current_move]
                move = moves[1].get_nowait()  # type: Path
                self._unitsMoves[unit] = (move, moves[1])
                current_move = move
            except Empty:
                self._unitsMoves[unit] = (None, moves[1])
                current_move = None
            except:
                traceback.print_exc()
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

    def _handleEvent(self, unit: MovingUnit, event) -> None:
        """
        The goal of this method is to handle the given event for the given unit

        Args:
            unit: The unit that sent the event through its linker
            event: The event sent by the controller
        """
        try:
            move = self.game.createMoveForDescriptor(unit, event)  # May raise: UnfeasibleMoveException
            self._movesEvent[move] = event
            self._addMove(unit, move)
        except UnfeasibleMoveException:
            pass
        except:
            traceback.print_exc()

    def _getPipeConnection(self, linker: Linker) -> PipeConnection:
        return self.linkersConnection[linker]

    def _getUnitFromLinker(self, linker: Linker) -> MovingUnit:
        return self.linkers[linker]

    def _informBotOnPerformedMove(self, moved_unit_number: int, move: Path):
        for linker in self.linkers:
            if issubclass(type(linker), BotLinker):
                event = self._movesEvent[move]
                pipe_conn = self._getPipeConnection(linker)
                try:
                    pipe_conn.send(BotEvent(moved_unit_number, event))
                except:
                    traceback.print_exc()

    def _getProcessPipeConnection(self, linker):
        return self.linkersProcessConnection[linker]

    def _killUnit(self, unit: MovingUnit, linker: Linker):
        unit.kill()
        if not unit.isAlive():
            self.linkersInfoConnection[linker].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))
