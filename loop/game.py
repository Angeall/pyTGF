from abc import ABCMeta, abstractmethod
from queue import Queue, Empty

import pygame
from pygame.locals import *

from characters.controller import Controller
from characters.controllers.human import Human
from characters.moves.path import Path
from characters.moves.move import IllegalMove, ImpossibleMove
from characters.units.moving_unit import MovingUnit
from characters.units.unit import Unit
from board.board import Board
from board.tile import Tile
from utils.geom import get_hypotenuse_length, get_polygon_radius

MAX_FPS = 60

CONTINUE = 0
PAUSE = 1
END = 2
FINISH = 3


class Game(metaclass=ABCMeta):
    def __init__(self, board: Board):
        self.board = board
        self._screen = None
        self._previouslyClickedTile = None
        self._gameStateChanged = False
        self._teamKill = False
        self._suicide = False
        self.winningPlayers = []
        self._state = CONTINUE  # The game must go on at start
        # self._teams -> keys: int; values: units
        self._teams = {}
        # self._units -> keys: Units; values: tile_ids
        self._units = {}  # type: dict
        # self._controllers -> keys: controllers; values: Units
        self._controllers = {}
        # self._controllersMoves -> keys: controllers; values: tuples (current_move, pending_moves)
        self._controllersMoves = {}
        # self._otherMoves -> keys: units; values: queue
        self._otherMoves = {}

    def setTeamKill(self, team_kill_enabled: bool = True):
        """
        Sets the team kill of the game. If true, a unit can harm another unit from its own team
        Args:
            team_kill_enabled: boolean that enables (True) or disables (False) the teamkill in the game
        """
        self._teamKill = team_kill_enabled

    def setSuicide(self, suicide_enabled: bool = True):
        """
        Sets the suicide handling of the game. If true, a unit can suicide itself on its own particles.
        Args:
            suicide_enabled: boolean that enables (True) or disables (False) the suicide in the game
        """
        self._suicide = suicide_enabled

    def run(self, max_fps: int = MAX_FPS) -> tuple:
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
        self._screen = pygame.display.set_mode(self.board.size, DOUBLEBUF + HWSURFACE)
        while self._state != END:
            self._handleInputs()
            if self._state == CONTINUE:
                self._handleControllersEvents()
                self._handlePendingMoves()
                self._refreshScreen()
                self._state = self._checkGameState()
            elif self._state == FINISH:
                return None
            clock.tick(max_fps)
        return self._handleGameFinished(self.winningPlayers)

    def addUnit(self, unit: Unit, controller: Controller, tile_id, initial_action: Path = None, team: int = -1) -> None:
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
        self._resizeUnit(unit, tile)
        unit.moveTo(tile.center)
        if initial_action is not None:
            self._handleControllerEvent(controller, initial_action)

    def _refreshScreen(self) -> None:
        """
        Update the visual state of the game
        """
        self.board.draw(self._screen)
        for unit in self._units:
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
            controller: The controller f*or which add a move
            move: The move to add for the given controller
        """
        if self._controllersMoves[controller][0] is not None:
            self._cancelCurrentMoves(controller)
        fifo = self._controllersMoves[controller][1]  # type: Queue
        fifo.put(move)
        # print((self._controllersMoves[controller][0], fifo))

    def _addOtherMove(self, unit: Unit, move: Path) -> None:
        """
        Adds a move that is NOT PERFORMED BY A CONTROLLER
        Args:
            unit: The unit that will be moved
            move: The move that will be performed
        """
        if unit not in self._otherMoves or self._otherMoves[unit] is None:
            self._otherMoves[unit] = move

    def _getUnitFromController(self, controller: Controller) -> MovingUnit:
        """
        Args:
            controller: The controller that controls the wanted unit

        Returns: The unit controlled by the given controller
        """
        return self._controllers[controller]

    def _getTileForUnit(self, unit: Unit) -> Tile:
        """
        Args:
            unit: The unit for which the Tile will be given

        Returns: The tile on which the given unit is located
        """
        return self.board.getTileById(self._units[unit])

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
            last_move.cancel()
            new_fifo.put(last_move)
        del fifo
        self._controllersMoves[controller] = (last_move, new_fifo)

    def _dispatchInputToHumanControllers(self, input_key) -> None:
        """
        Handles keyboard events and send them to Human Controllers to trigger actions if needed
        Args:
            input_key: The key pressed on the keyboard
        """
        for controller in self._controllers.keys():  # type: Human
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
            tile = self.board.getTileByPixel(pixel)
        self._previouslyClickedTile = tile
        mouse_state = pygame.mouse.get_pressed()
        for controller in self._controllers.keys():  # type: Human
            if issubclass(type(controller), Human):
                self._sendMouseEventToHumanController(controller, tile, mouse_state, click_up)

    def _handleControllersEvents(self) -> None:
        """
        Gets event from the controls and dispatch them to the right method
        """
        for controller in self._controllers.keys():
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
        for controller in self._controllers.keys():
            unit = self._controllers[controller]
            current_move = self._getNextMoveForControllerIfNeeded(controller)
            moved = self._handleMoveForUnit(unit, current_move, controller)
            if moved:
                moved_units.append(unit)

        for unit in self._otherMoves:  # type: Unit
            if unit not in moved_units:  # Two moves on the same unit cannot be performed at the same time...
                unit_controller = None
                for controller in self._controllers:
                    if self._controllers[controller] is unit:
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
                        self._updateGameState(controller, tile_id)
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
                current_move.cancel(cancel_post_action=True)
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
                move = moves[1].get_nowait()  # type: Path
                self._controllersMoves[controller] = (move, moves[1])
                current_move = move
            except Empty:
                self._controllersMoves[controller] = (None, moves[1])
                current_move = None
        return current_move

    def _updateGameState(self, controller, tile_id):
        """
        Change the unit's tile and checks for collisions
        Args:
            controller: The controller to update
            tile_id: The new tile id to link with the given controller
        """
        unit = self._controllers[controller]
        self._units[unit] = tile_id
        new_tile = self.board.getTileById(tile_id)
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

    def _handleCollision(self, unit, other_units) -> None:
        """
        Handles a collision between a unit and other units
        Args:
            unit: The moving units
            other_units: The other units that are on the same tile than the moving unit
        """
        for other_unit in other_units:
            if not (unit is other_unit):
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

    def _collidePlayers(self, player1, player2, frontal: bool = False):
        """
        Makes what it has to be done when the first given player collides with a particle of the second given player
        (Careful : two moving units (alive units) colliding each other causes a frontal collision that hurts both
        units)
        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
        """
        same_team = self._fromSameTeam(player1, player2)
        suicide = player1 is player2
        if (not same_team or self._teamKill) or (suicide and self._suicide):
            player1.kill()
            if frontal:
                player2.kill()

    def _checkGameState(self) -> int:
        """
        Checks if the game is finished
        Returns: 0 = CONTINUE; 2 = END
        """
        state = self._isFinished()
        if state[0]:
            self.winningPlayers = state[1]
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

    def _handleGameFinished(self, winning_units: list) -> tuple:
        """
        Handle the end of the game
        Args:
            winning_units: The units that won the game

        Returns: A tuple containing the winning units or an empty tuple if there is a draw
        """
        winning_player_numbers = []
        if winning_units is not None:
            for unit in winning_units:
                winning_player_numbers.append(unit.playerNumber)
        return tuple(winning_player_numbers)

    @staticmethod
    def _resizeUnit(unit: Unit, tile: Tile) -> None:
        """
        Resize a unit to fit the given tile
        Args:
            unit: The unit to resize
            tile: The tile to fit in
        """
        multiply_ratio = tile.sideLength / max(unit.sprite.rect.height, unit.sprite.rect.width)
        hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                           unit.sprite.rect.width * multiply_ratio)
        tile_diameter = get_polygon_radius(tile.nbrOfSides, tile.sideLength) * 2
        while hypotenuse > tile_diameter:
            multiply_ratio *= 0.99
            hypotenuse = get_hypotenuse_length(unit.sprite.rect.height * multiply_ratio,
                                               unit.sprite.rect.width * multiply_ratio)
        unit.sprite.size(int(round(unit.sprite.rect.width * multiply_ratio)),
                         int(round(unit.sprite.rect.height * multiply_ratio)))

    @abstractmethod
    def _isFinished(self) -> (bool, list):
        """
        Checks if the game is finished and returns the winning units or None if the game drew
        Returns: a tuple : (bool telling if the game is finished, Units the winning units or None if draw or unfinished)
        """
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

    @abstractmethod
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
        pass

    @abstractmethod
    def _sendInputToHumanController(self, controller: Human, input_key: int) -> None:
        """
        Can optionally filter the keyboard events to send
        Args:
            controller: The controller to which the event must be sent
            input_key: The key pressed on the keyboard
        """
        pass
