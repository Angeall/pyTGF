from abc import ABCMeta, abstractmethod
from queue import Queue, Empty

import pygame
from pygame.locals import *

from characters.controller import Controller
from characters.controllers.human import Human
from characters.moves.path import Path
from characters.units.unit import Unit
from display.board import Board
from display.tile import Tile

MAX_FPS = 60

CONTINUE = 0
PAUSE = 1
END = 2


class Game(metaclass=ABCMeta):

    def __init__(self, board: Board):
        self.board = board
        self._screen = None
        self._previouslyClickedTile = None
        self._gameStateChanged = False
        self._teamKill = False
        self._state = CONTINUE  # The game must go on at start
        # self._teams -> keys: int; values: units
        self._teams = {}
        # self._units -> keys: Units; values: tile_ids
        self._units = {}  # type: dict
        # self._controllers -> keys: controllers; values: _units
        self._controllers = {}
        # self._controllersMoves -> keys: controllers; values: tuples (current_move, pending_moves)
        self._controllersMoves = {}

    def setTeamKill(self, team_kill_enabled: bool=True):
        self._teamKill = team_kill_enabled

    def run(self, max_fps: int=MAX_FPS):
        pygame.init()
        clock = pygame.time.Clock()
        self._screen = pygame.display.set_mode(self.board.size, DOUBLEBUF + HWSURFACE)
        while self._state != END:
            self._state = self._handleInputs()
            if self._state == PAUSE:
                self.pause()
            elif self._state == CONTINUE:
                self._handleControllersEvents()
                self._handlePendingMoves()
                self._refreshScreen()
                self._state = self._checkGameState()
            clock.tick(max_fps)

    def addUnit(self, unit: Unit, controller: Controller, tile_id, initial_action: Path=None, team: int=-1) -> None:
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
        self._controllers[controller] = unit
        self._controllersMoves[controller] = (None, Queue())
        self._units[unit] = tile_id
        if team in self._teams.keys():
            self._teams[team].append(unit)
        else:
            self._teams[team] = [unit]
        tile = self.board.getTileById(tile_id)
        tile.addOccupant(unit)
        unit.moveTo(tile.center)
        if initial_action is not None:
            self._handleControllerEvent(controller, initial_action)

    def _refreshScreen(self):
        self.board.draw(self._screen)
        pygame.display.flip()

    def _handleInputs(self) -> int:
        """
        Handles all the user input (mouse and keyboard)
        Returns: The new game state : 0 = Continue, 1 = Pause and 2 = End
        """
        for event in pygame.event.get():
            if event.type == QUIT:
                return END
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return PAUSE
                else:
                    self._dispatchInputToHumanControllers(event.key)
            elif event.type == MOUSEBUTTONDOWN:
                self._dispatchMouseEventToHumanControllers(event.pos)
            elif event.type == MOUSEBUTTONUP:
                self._dispatchMouseEventToHumanControllers(None, click_up=True)
        return CONTINUE

    def _addMove(self, controller: Controller, move: Path) -> None:
        """
        Adds a move (cancelling the pending moves)
        Args:
            controller: The controller f*or which add a move
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
            move_tuple = self._controllersMoves[controller] # type: tuple
            fifo = move_tuple[1]  # type: Queue
            last_move = move_tuple[0]  # type: Path
            new_fifo = Queue()
            if last_move is not None:
                last_move.cancel()
                new_fifo.put(last_move)
            del fifo
            self._controllersMoves[controller] = (last_move, new_fifo)
        except Empty:
            pass

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
            current_move = self._getNextMoveForControllerIfNeeded(controller)
            if current_move is not None:
                tile_id = current_move.performNextMove()
                if tile_id is not None:  # A new tile has been reached by the movement
                    self._updateGameState(controller, tile_id)
                if current_move.cancelled or current_move.completed:
                    pass  # TODO check for collisions

    def _getNextMoveForControllerIfNeeded(self, controller) -> Path:
        """
        Checks if a move is available for the given controller, and if so, returns it
        Args:
            controller: The given controller

        Returns: The next move if it is available, and None otherwise
        """
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
        return current_move

    def _updateGameState(self, controller, tile_id):
        unit = self._controllers[controller]
        old_tile_id = self._units[unit]
        self._units[unit] = tile_id
        tile = self.board.getTileById(old_tile_id)
        if unit in tile.occupants:
            tile.removeOccupant(unit)
        new_tile = self.board.getTileById(tile_id)
        new_tile.addOccupant(unit)
        if new_tile.hasTwoOrMoreOccupants():
            self._handleCollision(unit, new_tile.occupants)
        self._gameStateChanged = True

    def _fromSameTeam(self, unit1, unit2):
        """
        Checks if the two given units are in the same team
        Args:
            unit1: The first unit to check
            unit2: The second unit to check

        Returns: True if the two units are in the same team
        """
        for team in self._teams.keys():
            team_units = self._teams[team]
            if unit1 in team_units:
                if unit2 in team_units:
                    return True
                else:  # unit 1 in team, but not unit 2
                    return False
            elif unit2 in team_units:  # unit 2 in team units, but not unit 1
                return False
        return False  # Never found the team...

    def _handleCollision(self, unit, other_units):
        for other_unit in other_units:
            if other_unit in self._units.keys():  # If the other unit is a controlled unit
                self._collidePlayers(unit, other_unit, frontal=True)
            else:  # If the other unit is a Particle
                other_player = None
                for player in self._units.keys():  # type: Unit
                    if player.hasParticle(other_unit):
                        other_player = player
                        break
                if other_player is not None:  # If we found the player to which belongs the colliding particle
                    self._collidePlayers(unit, other_player)

    def _collidePlayers(self, player1, player2, frontal: bool=False):
        """
        Makes what it has to be done when the first given player collides with a particle of the second given player
        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
        """
        same_team = self._fromSameTeam(player1, player2)
        if not same_team or self._teamKill:  # If not same team or the team kill is activated: kill each other
            player1.kill()
            if frontal:
                player2.kill()

    @abstractmethod
    def _isFinished(self) -> (bool, list):
        """
        Checks if the game is finished and returns the winning units or None if the game drew
        Returns: a tuple : (bool telling if the game is finished, Units the winning units or None if draw or unfinished)
        """
        pass

    @abstractmethod
    def _handleGameFinished(self, winning_units: list):
        """
        Handle the end of the game
        Args:
            winning_units: The units that won the game
        """
        pass

    def _checkGameState(self) -> int:
        state = self._isFinished()
        if state[0]:
            self._handleGameFinished(state[1])
            return END
        return CONTINUE

    def pause(self):
        self._state = PAUSE

    def resume(self):
        """
        Resume the game
        Returns:
        """
        self._state = CONTINUE


