"""
Fie containing the definition of the logical loop of a game, containing all the input events handling,
and the bot controllers handling
"""

import time
from queue import Queue, Empty
from typing import Dict, Optional, NewType
from typing import Tuple
from typing import Union

import pygame
from multiprocess.connection import Pipe

try:
    from multiprocess.connection import PipeConnection
except ImportError:
    PipeConnection = NewType("PipeConnection", object)
from pathos.pools import ProcessPool as Pool
from pygame.constants import DOUBLEBUF, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT

from pytgf.board import TileIdentifier
from pytgf.characters.moves import IllegalMove, ImpossibleMove, Path, MoveDescriptor
from pytgf.characters.units import MovingUnit, Unit
from pytgf.controls.events import BotEvent, SpecialEvent
from pytgf.controls.linkers import Linker, HumanLinker, BotLinker
from pytgf.game import Game, UnfeasibleMoveException
from pytgf.utils.geom import Coordinates
from pytgf.utils.unit import resize_unit

__author__ = 'Anthony Rouneau'

CONTINUE = 0
PAUSE = 1
END = 2
FINISH = 3
MAX_FPS = 30


class MainLoop:
    """
    Defines the logical loop of a game, running MAX_FPS times per second, sending the inputs to the HumanLinker, and the
    game updates to the BotLinkers.
    """
    def __init__(self, game: Game):
        """
        Instantiates the logical loop

        Args:
            game: The game to run in this loop
        """
        self.game = game
        self.game.addCustomMoveFunc = self._addCustomMove
        self._screen = None
        self._state = CONTINUE  # The game must go on at start

        self.linkersConnection = {}  # type: Dict[Linker, PipeConnection]
        self.linkersInfoConnection = {}  # type: Dict[Linker, PipeConnection]

        self.linkers = {}  # type: Dict[Linker, MovingUnit]
        self._unitsMoves = {}  # type: Dict[MovingUnit, Tuple[Path, Queue]]
        self._movesEvent = {}  # type: Dict[Path, MoveDescriptor]
        self._otherMoves = {}  # type: Dict[Unit, Path]
        self._killSent = {}  # Used to maintain the fact that the kill event has been sent
        self.executor = None
        self._prepared = False

    # -------------------- PUBLIC METHODS -------------------- #

    def run(self, max_fps: int=MAX_FPS) -> Union[None, Tuple[MovingUnit, ...]]:
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
        assert self.game.board.graphics is not None
        try:
            self._screen = pygame.display.set_mode(self.game.board.graphics.size, DOUBLEBUF)
        except pygame.error:  # No video device
            pass
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

    def addUnit(self, unit: MovingUnit, linker: Linker, tile_id: TileIdentifier, initial_action: Path=None,
                team: int=-1) -> None:
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
        self.game.addUnit(unit, team, tile_id)
        self._addLinker(linker, unit)
        self._unitsMoves[unit] = (None, Queue())
        tile = self.game.board.getTileById(tile_id)
        resize_unit(unit, self.game.board)
        unit.moveTo(tile.center)
        if initial_action is not None:
            unit.currentAction = initial_action
            self._handleEvent(unit, initial_action)

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

    # -------------------- PROTECTED METHODS -------------------- #

    def _refreshScreen(self) -> None:
        """
        Update the visual state of the game
        """
        try:
            if self._screen is None:
                raise pygame.error("No Video device")
            self.game.board.draw(self._screen)
            for unit in self.linkers.values():
                if unit.isAlive():
                    unit.draw(self._screen)
            pygame.display.flip()
        except pygame.error:  # No video device
            pass

    def _handleInputs(self) -> None:
        """
        Handles all the user input (mouse and keyboard)
        """
        try:
            events_got = pygame.event.get()
        except pygame.error:  # No video device
            events_got = []
        for event in events_got:
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

    def _addCustomMove(self, unit: Unit, move: Path, event: MoveDescriptor) -> None:
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
        move_tuple = self._unitsMoves[unit]
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

    def _dispatchMouseEventToHumanControllers(self, pixel: Optional[Coordinates], click_up=False) -> None:
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

        for unit in self._otherMoves:  # type: MovingUnit
            unit_linker = None
            for linker in self.linkers:
                if self._getUnitFromLinker(linker) is unit:
                    unit_linker = linker
            if unit_linker is not None:
                if self._otherMoves[unit] is not None:
                    moved = self._handleMoveForUnit(unit, self._otherMoves[unit], unit_linker)
                    if moved:
                        moved_units.append(unit)
                    if self._otherMoves[unit].finished():
                        self._otherMoves[unit] = None

        for linker in self.linkers:  # type: Linker
            unit = self._getUnitFromLinker(linker)
            if unit not in moved_units:  # Two moves on the same unit cannot be performed at the same time...
                if not unit.isAlive() and (unit not in self._killSent or not self._killSent[unit]):
                    self.linkersInfoConnection[linker].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))
                    self._killSent[unit] = True
                current_move = self._getNextMoveForUnitIfAvailable(unit)
                self._handleMoveForUnit(unit, current_move, linker)
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
                    if isinstance(current_move, Path):
                        del self._movesEvent[current_move]
                move = moves[1].get_nowait()  # type: Path
                self._unitsMoves[unit] = (move, moves[1])
                current_move = move
            except Empty:
                self._unitsMoves[unit] = (None, moves[1])
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

    def _handleEvent(self, unit: MovingUnit, event: MoveDescriptor) -> None:
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

    def _getPipeConnection(self, linker: Linker) -> PipeConnection:
        """
        Args:
            linker: The linker for which we want the pipe connection

        Returns: The pipe connection to send and receive game updates
        """
        return self.linkersConnection[linker]

    def _getUnitFromLinker(self, linker: Linker) -> MovingUnit:
        """
        Args:
            linker: The linker for which we want the unit

        Returns: The unit for the given linker
        """
        return self.linkers[linker]

    def _informBotOnPerformedMove(self, moved_unit_number: int, move: Path) -> None:
        """
        Update the game state of the bot controllers

        Args:
            moved_unit_number: The number representing the unit that moved and caused the update
            move: The move that caused the update
        """
        for linker in self.linkers:
            if issubclass(type(linker), BotLinker):
                event = self._movesEvent[move]
                pipe_conn = self._getPipeConnection(linker)
                pipe_conn.send(BotEvent(moved_unit_number, event))

    def _killUnit(self, unit: MovingUnit, linker: Linker) -> None:
        """
        Kills the given unit and tells its linker

        Args:
            unit: The unit to kill
            linker: The linker, to which tell that the unit is dead
        """
        unit.kill()
        if not unit.isAlive():
            self.linkersInfoConnection[linker].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))

    def _addCollaborationPipes(self, linker: BotLinker) -> None:
        """
        Adds the collaboration pipes between the given linker and its teammate's

        Args:
            linker: The linker to connect with its teammate
        """
        for teammate in self.game.teams[self.game.unitsTeam[self.linkers[linker]]]:
            if teammate is not self.linkers[linker]:
                teammate_linker = None  # type: BotLinker
                for other_linker in self.linkers:
                    if self.linkers[other_linker] is teammate:
                        teammate_linker = other_linker
                        break
                pipe1, pipe2 = Pipe()
                linker.addCollaborationPipe(teammate_linker.controller.playerNumber, pipe1)
                teammate_linker.addCollaborationPipe(linker.controller.playerNumber, pipe2)

    def _prepareLoop(self) -> None:
        """
        Launches the processes of the AIs
        """
        self.executor = Pool(len(self.linkers))
        try:
            self.executor.apipe(lambda: None)
        except ValueError:
            self.executor.restart()
        for linker in self.linkers:
            if isinstance(linker, BotLinker):
                linker.controller.gameState = self.game.copy()
            self.executor.apipe(linker.run)
        time.sleep(2)  # Waiting for the processes to launch correctly
        self._prepared = True

    def _addLinker(self, linker: Linker, unit: MovingUnit) -> None:
        """
        Adds the linker to the loop, creating the pipe connections

        Args:
            linker: The linker to add
            unit: The unit, linked by this linker
        """
        self.linkers[linker] = unit
        parent_conn, child_conn = Pipe()
        parent_info_conn, child_info_conn = Pipe()
        self.linkersConnection[linker] = parent_conn
        self.linkersInfoConnection[linker] = parent_info_conn
        linker.setMainPipe(child_conn)
        linker.setGameInfoPipe(child_info_conn)
        if isinstance(linker, BotLinker):
            self._addCollaborationPipes(linker)
