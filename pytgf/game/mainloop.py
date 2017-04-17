"""
Fie containing the definition of the logical loop of a game, containing all the input events handling,
and the bot controllers handling
"""

import time
from queue import Queue, Empty
from typing import Dict, Optional, List
from typing import Tuple
from typing import Union

import pygame
from multiprocess.connection import Pipe

from pytgf.controls.events.multiple import MultipleEvents
from pytgf.controls.events.wake import WakeEvent

try:
    from multiprocess.connection import PipeConnection
except ImportError:
    PipeConnection = object
from pathos.pools import ProcessPool as Pool
from pygame.constants import DOUBLEBUF, MOUSEBUTTONDOWN, MOUSEBUTTONUP, K_ESCAPE, KEYDOWN, QUIT

from pytgf.board import TileIdentifier
from pytgf.characters.moves import IllegalMove, ImpossibleMove, Path, MoveDescriptor
from pytgf.characters.units import Unit
from pytgf.controls.events import BotEvent, SpecialEvent, Event
from pytgf.controls.wrappers import ControllerWrapper, HumanControllerWrapper, BotControllerWrapper
from pytgf.game import API, UnfeasibleMoveException
from pytgf.utils.geom import Coordinates
from pytgf.characters.utils.units import resize_unit

__author__ = 'Anthony Rouneau'

CONTINUE = 0
PAUSE = 1
END = 2
FINISH = 3
MAX_FPS = 30


MOVE_COMPLETED = 0
MOVE_JUST_STARTED = 1
MOVE_IN_PROGRESS = 2
MOVE_ILLEGAL = -1
MOVE_IMPOSSIBLE = -2
MOVE_FAILED = -3


class MainLoop:
    """
    Defines the logical loop of a game, running MAX_FPS times per second, sending the inputs to the HumanControllerWrapper, and the
    game updates to the BotControllerWrappers.
    """

    def __init__(self, api: API, turn_by_turn: bool = False):
        """
        Instantiates the logical loop

        Args:
            api: The game to run in this loop
        """
        self.api = api
        self.game = api.game
        self.game.addCustomMoveFunc = self._addCustomMove
        self.game.turnByTurn = turn_by_turn
        self._currentTurnTaken = False
        self._screen = None
        self._state = CONTINUE  # The game must go on at start
        self._eventsToSend = {}  # type: Dict[ControllerWrapper, List[Event]]

        self.wrappersConnection = {}  # type: Dict[ControllerWrapper, PipeConnection]
        self.wrappersInfoConnection = {}  # type: Dict[ControllerWrapper, PipeConnection]

        self.wrappers = {}  # type: Dict[ControllerWrapper, Unit]
        self._unitsMoves = {}  # type: Dict[Unit, Tuple[Path, Queue]]
        self._moveDescriptors = {}  # type: Dict[Path, MoveDescriptor]
        self._otherMoves = {}  # type: Dict[Unit, Path]
        self._killSent = {}  # Used to maintain the fact that the kill event has been sent
        self.executor = None
        self._prepared = False

    # -------------------- PUBLIC METHODS -------------------- #

    def run(self, max_fps: int = MAX_FPS) -> Union[None, Tuple[Unit, ...]]:
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
            clock.tick(max_fps)
            self._handleInputs()
            if self._state == FINISH:
                self.executor.terminate()
                self._prepared = False
                return None
            elif self._state != PAUSE:
                self._state = self._checkGameState()
                if self._state == CONTINUE:
                    self._getNextMoveFromControllerWrapperIfAvailable()
                    self._handlePendingMoves()
                    self._refreshScreen()
        self.executor.terminate()
        self._prepared = False
        return self.game.winningPlayers

    def addUnit(self, unit: Unit, wrapper: ControllerWrapper, tile_id: TileIdentifier,
                initial_action: MoveDescriptor = None, team: int = -1) -> None:
        """
        Adds a unit to the game, located on the tile corresponding
        to the the given tile id and controlled by the given controller

        Args:
            unit: The unit to add to the game
            wrapper: The linker of that unit
            tile_id: The identifier of the tile it will be placed on
            initial_action: The initial action of the unit
            team: The number of the team this player is in (-1 = no team)
        """
        is_controlled = wrapper is not None
        self.game.addUnit(unit, team, tile_id, controlled=is_controlled)
        if is_controlled:
            self._addControllerWrapper(wrapper, unit)
            if initial_action is None and (not self.api.isTurnByTurn() or
                                           unit.playerNumber == self.api.getCurrentPlayer()):
                self._eventsToSend[wrapper].append(WakeEvent())
        self._unitsMoves[unit] = (None, Queue())
        tile = self.game.board.getTileById(tile_id)
        resize_unit(unit, self.game.board)
        unit.moveTo(tile.center)
        if initial_action is not None:
            unit.setLastAction(initial_action)
            self._handleEvent(unit, initial_action, wrapper.controller.playerNumber)

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
            drawn_units = []
            for unit in self.wrappers.values():
                if unit.isAlive():
                    unit.draw(self._screen)
                    drawn_units.append(unit)
            for unit in self.game.unitsLocation:
                if unit.isAlive() and unit not in drawn_units:
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

    def _addMove(self, unit: Unit, move: Path) -> None:
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
        print("other move added")
        if unit not in self._otherMoves or self._otherMoves[unit] is None:
            self._otherMoves[unit] = move
        self._moveDescriptors[move] = event

    def _cancelCurrentMoves(self, unit: Unit) -> None:
        """
        Cancel the current movement if there is one and remove all the other pending movements.

        Args:
            unit: The unit for which cancel the movements
        """
        if unit in self._unitsMoves:
            move_tuple = self._unitsMoves[unit]
            fifo = move_tuple[1]  # type: Queue
            last_move = move_tuple[0]  # type: Path
            new_fifo = Queue()
            if last_move is not None:
                last_move.stop()
            while True:
                try:
                    move = fifo.get_nowait()
                    del self._moveDescriptors[move]
                except Empty:
                    break
            self._unitsMoves[unit] = (last_move, new_fifo)

    def _dispatchInputToHumanControllers(self, input_key) -> None:
        """
        Handles keyboard events and send them to Human Controllers to trigger actions if needed

        Args:
            input_key: The key pressed on the keyboard
        """
        for linker in self.wrappers:  # type: HumanControllerWrapper
            if issubclass(type(linker), HumanControllerWrapper):
                self._getPipeConnection(linker).send(
                    self.game.createKeyboardEvent(self._getUnitFromControllerWrapper(linker),
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
        for linker in self.wrappers:  # type: ControllerWrapper
            if issubclass(type(linker), HumanControllerWrapper):
                tile_id = None
                if tile is not None:
                    tile_id = tile.identifier
                self._getPipeConnection(linker).send(
                    self.game.createMouseEvent(self._getUnitFromControllerWrapper(linker),
                                               pixel, mouse_state, click_up, tile_id))

    def _getNextMoveFromControllerWrapperIfAvailable(self) -> None:
        """
        Gets event from the controllers and dispatch them to the right method
        """
        for current_wrapper in self.wrappersConnection:  # type: ControllerWrapper
            pipe_conn = self._getPipeConnection(current_wrapper)
            if pipe_conn.poll():
                move = pipe_conn.recv()
                if not self.game.turnByTurn or (self.api.isCurrentPlayer(current_wrapper.controller.playerNumber)
                                                and not self._currentTurnTaken):
                    self._handleEvent(self.wrappers[current_wrapper], move, current_wrapper.controller.playerNumber)

    def _handlePendingMoves(self) -> None:
        """
        Get the next move to be performed and perform its next step
        """
        moved_units = []

        completed_moves = {}  # type: Dict[Unit, Tuple[TileIdentifier, MoveDescriptor]]
        just_started = {}  # type: Dict[int, MoveDescriptor]
        illegal_moves = []  # type: List[Unit]
        impossible_moves = {}  # type: List[Unit]

        self._handleOtherMoves(completed_moves, illegal_moves, impossible_moves, just_started, moved_units)
        self._handleMoves(completed_moves, illegal_moves, impossible_moves, just_started, moved_units)
        self._updateFromMoves(completed_moves, illegal_moves, impossible_moves, just_started)

    def _updateFromMoves(self, completed_moves, illegal_moves, impossible_moves, just_started):
        for unit, (tile_id, move_descriptor) in completed_moves.items():
            self.game.updateGameState(unit, tile_id, move_descriptor)
        for player_number, move_descriptor in just_started.items():
            self.game.getUnitForNumber(player_number).setCurrentAction(move_descriptor)
            self._addMessageToSendToAll(player_number, move_descriptor)
            if self.api.isTurnByTurn():
                self._sendEventsToNextPlayer()
        if not self.api.isTurnByTurn():
            self._sendEventsToAll()
        for unit in illegal_moves:
            self.game.unitsLocation[unit] = self.game.board.OUT_OF_BOARD_TILE.identifier
            self._killUnit(unit, self._getWrapperFromPlayerNumber(unit.playerNumber))
            # self.game.checkIfFinished()
            self._cancelCurrentMoves(unit)
        for unit in impossible_moves:
            self._cancelCurrentMoves(unit)
        self.game.checkIfFinished()

    def _handleMoves(self, completed_moves, illegal_moves, impossible_moves, just_started, moved_units):
        for wrapper in self.wrappers:  # type: ControllerWrapper
            unit = self._getUnitFromControllerWrapper(wrapper)
            if unit not in moved_units:  # Two moves on the same unit cannot be performed at the same time...
                if not unit.isAlive() and (unit not in self._killSent or not self._killSent[unit]):
                    self.wrappersInfoConnection[wrapper].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))
                    self._killSent[unit] = True
                current_move = self._getNextMoveForUnitIfAvailable(unit)
                if current_move is not None:
                    move_state = self._performNextStepOfMove(current_move.unit, current_move)
                    self._fillMoveStructures(completed_moves, just_started, illegal_moves, impossible_moves,
                                             current_move, move_state)

    def _handleOtherMoves(self, completed_moves, illegal_moves, impossible_moves, just_started, moved_units):
        for unit in self._otherMoves:  # type: Unit
            move = self._otherMoves[unit]
            if move is not None:
                move_state = self._performNextStepOfMove(move.unit, move)
                if move_state != MOVE_FAILED:
                    moved_units.append(move.unit)
                if move.finished():
                    self._otherMoves[unit] = None
                self._fillMoveStructures(completed_moves, just_started, illegal_moves, impossible_moves, move,
                                         move_state)

    def _fillMoveStructures(self, completed_moves: Dict[Unit, Tuple[TileIdentifier, MoveDescriptor]],
                            just_started: Dict[int, MoveDescriptor], illegal_moves: List[Unit],
                            impossible_moves: List[Unit], move: Path, move_state: int):
        """
        Takes a move's state and the data structures of the performed moves in this iteration an fill them
         following the state's value
         
        Args:
            completed_moves: The dict containing the units that completed a move along with their new tile_id 
            just_started: 
                The dict containing the number of the units that started a move, 
                along with the descriptor of the started move
            illegal_moves: The list containing all the units that performed an illegal move this iteration  
            impossible_moves: The list containing all the units that performed an impossible move this iteration  
            move: The performed move
            move_state: The state of the performed move
        """
        if move_state == MOVE_COMPLETED:
            completed_moves[move.unit] = (move.reachedTileIdentifier,  self._moveDescriptors[move])
        elif move_state == MOVE_JUST_STARTED:
            just_started[move.unit.playerNumber] = self._moveDescriptors[move]
        elif move_state == MOVE_ILLEGAL:
            illegal_moves.append(move.unit)
        elif move_state == MOVE_IMPOSSIBLE:
            impossible_moves.append(move.unit)

    def _addMessageToSendToAll(self, moved_unit_number: int, move_descriptor: MoveDescriptor):
        """
        Adds a message to the message queue of each ControllerWrapper
        
        Args:
            moved_unit_number: The number representing the unit that moved 
            move_descriptor: The descriptor of the performed move
        """
        for wrapper in self._eventsToSend:
            self._eventsToSend[wrapper].append(BotEvent(moved_unit_number, move_descriptor))

    @staticmethod
    def _performNextStepOfMove(unit: Unit, current_move: Path) -> int:
        """
        Perform the next step of the given move on the given unit

        Args:
            unit: The unit that performs the move
            current_move: The current move to perform
        
        Returns:
            A couple of booleans. The first indicating that the move has been completed and the second indicating that
            the move has just started
        """
        if unit.isAlive():
            if current_move is not None:
                try:
                    just_started, move_completed, tile_id = current_move.performNextMove()
                    if move_completed:  # A new tile has been reached by the movement
                        return MOVE_COMPLETED
                    elif just_started:
                        return MOVE_JUST_STARTED
                    return MOVE_IN_PROGRESS
                except IllegalMove:
                    return MOVE_ILLEGAL
                except ImpossibleMove:
                    return MOVE_IMPOSSIBLE
        else:
            if current_move is not None:
                current_move.stop(cancel_post_action=True)
        return MOVE_FAILED

    def _getNextMoveForUnitIfAvailable(self, unit: Unit) -> Union[Path, None]:
        """
        Checks if a move is available for the given controller, and if so, returns it

        Args:
            unit: The given

        Returns: The next move if it is available, and None otherwise
        """
        # if self._turnByTurn and not unit.playerNumber == self._playersOrder[self._currentPlayerIndex]:
        #     return None  # Sorry, not your turn to play !
        moves = self._unitsMoves[unit]
        current_move = moves[0]  # type: Path
        if current_move is None or current_move.finished():
            try:
                if current_move is not None:
                    if isinstance(current_move, Path):
                        if self.api.isTurnByTurn():
                            self.api.switchToNextPlayer()
                            self._currentTurnTaken = False
                        del self._moveDescriptors[current_move]
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

    def _handleEvent(self, unit: Unit, event: MoveDescriptor, player_number: int) -> None:
        """
        The goal of this method is to handle the given event for the given unit

        Args:
            unit: The unit that sent the event through its linker
            event: The event sent by the controller
        """
        try:
            move = self.api.createMoveForDescriptor(unit, event)  # may raise: UnfeasibleMoveException
            self._currentTurnTaken = True
            self._moveDescriptors[move] = event
            self._addMove(unit, move)
        except UnfeasibleMoveException:
            self._sendEventsToController(player_number, event=WakeEvent())

    def _getPipeConnection(self, linker: ControllerWrapper) -> PipeConnection:
        """
        Args:
            linker: The linker for which we want the pipe connection

        Returns: The pipe connection to send and receive game updates
        """
        return self.wrappersConnection[linker]

    def _getWrapperFromPlayerNumber(self, player_number: int):
        """
        Retrieves the wrapper from the given player number
        
        Args:
            player_number: The number representing the player for which we want the wrapper 

        Returns: The wrapper that wraps the controller of the given player
        """
        found = None
        for wrapper in self.wrappersConnection:
            if wrapper.controller.playerNumber == player_number:
                found = wrapper
                break
        return found

    def _getUnitFromControllerWrapper(self, linker: ControllerWrapper) -> Unit:
        """
        Args:
            linker: The linker for which we want the unit

        Returns: The unit for the given linker
        """
        return self.wrappers[linker]

    def _sendEventsToNextPlayer(self):
        """
        Send the events waiting to the next player to play
        """
        next_player_number = self.api.getNextPlayer()
        self._sendEventsToController(next_player_number)

    def _sendEventsToController(self, player_number: int, event: Event=None):

        next_player_wrapper = self._getWrapperFromPlayerNumber(player_number)
        pipe_conn = self._getPipeConnection(next_player_wrapper)
        if event is None:
            event = MultipleEvents(self._eventsToSend[next_player_wrapper])
        pipe_conn.send(event)
        self._eventsToSend[next_player_wrapper] = []

    def _sendEventsToAll(self):
        for player_number in self.api.getPlayerNumbers():
            self._sendEventsToController(player_number)

    def _informBotOnPerformedMove(self, moved_unit_number: int, move_descriptor: MoveDescriptor) -> None:
        """
        Update the game state of the bot controllers

        Args:
            moved_unit_number: The number representing the unit that moved and caused the update
            move_descriptor: The move that caused the update
        """
        for wrapper in self.wrappers:
            if issubclass(type(wrapper), BotControllerWrapper):
                pipe_conn = self._getPipeConnection(wrapper)
                pipe_conn.send(BotEvent(moved_unit_number, move_descriptor))

    def _killUnit(self, unit: Unit, linker: ControllerWrapper) -> None:
        """
        Kills the given unit and tells its linker

        Args:
            unit: The unit to kill
            linker: The linker, to which tell that the unit is dead
        """
        unit.kill()
        if not unit.isAlive():
            self.wrappersInfoConnection[linker].send(SpecialEvent(flag=SpecialEvent.UNIT_KILLED))

    def _addCollaborationPipes(self, linker: BotControllerWrapper) -> None:
        """
        Adds the collaboration pipes between the given linker and its teammate's

        Args:
            linker: The linker to connect with its teammate
        """
        for teammate in self.game.teams[self.game.unitsTeam[self.wrappers[linker]]]:
            if teammate is not self.wrappers[linker]:
                teammate_linker = None  # type: BotControllerWrapper
                for other_linker in self.wrappers:
                    if self.wrappers[other_linker] is teammate:
                        teammate_linker = other_linker
                        break
                pipe1, pipe2 = Pipe()
                linker.addCollaborationPipe(teammate_linker.controller.playerNumber, pipe1)
                teammate_linker.addCollaborationPipe(linker.controller.playerNumber, pipe2)

    def _prepareLoop(self) -> None:
        """
        Launches the processes of the AIs
        """
        self.executor = Pool(len(self.wrappers))
        try:
            self.executor.apipe(lambda: None)
        except ValueError:
            self.executor.restart()
        for linker in self.wrappers:
            if isinstance(linker, BotControllerWrapper):
                linker.controller.gameState = self.game.copy()
            self.executor.apipe(linker.run)
        time.sleep(2)  # Waiting for the processes to launch correctly
        self._prepared = True

    def _addControllerWrapper(self, wrapper: ControllerWrapper, unit: Unit) -> None:
        """
        Adds the linker to the loop, creating the pipe connections

        Args:
            wrapper: The linker to add
            unit: The unit, linked by this linker
        """
        self.wrappers[wrapper] = unit
        parent_conn, child_conn = Pipe()
        parent_info_conn, child_info_conn = Pipe()
        self.wrappersConnection[wrapper] = parent_conn
        self.wrappersInfoConnection[wrapper] = parent_info_conn
        self._eventsToSend[wrapper] = []
        wrapper.setMainPipe(child_conn)
        wrapper.setGameInfoPipe(child_info_conn)
        if isinstance(wrapper, BotControllerWrapper):
            self._addCollaborationPipes(wrapper)
