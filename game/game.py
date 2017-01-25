import traceback
from abc import ABCMeta, abstractmethod
from functools import reduce
from types import FunctionType as function

from copy import deepcopy
from typing import Dict, List

import time

from characters.particle import Particle
from gameboard.board import Board, Tile
from characters.moves.path import Path
from characters.units.moving_unit import MovingUnit
from controls.events.keyboard import KeyboardEvent
from controls.events.mouse import MouseEvent


class InconsistentGameStateException(Exception):
    pass


class UnknownUnitException(Exception):
    pass


class UnfeasibleMoveException(Exception):
    pass


class Game(metaclass=ABCMeta):
    # TODO: add simulation capabilities. Careful to the units occupant update !
    def __init__(self, board: Board):
        """
        Creates a new Game using the given board

        Args:
            board:
                The board, containing the needed Tiles that will be used for the game.
                The units are added later on the board.
        """
        self.board = board
        self._finished = False
        self.winningPlayers = None
        self.teams = {}  # type: Dict[int, List[MovingUnit]]
        self.unitsTeam = {}  # type: Dict[MovingUnit, int]
        self.players = {}  # type: Dict[int, MovingUnit]
        self.unitsLocation = {}   # type: Dict[Particle, tuple]
        self._previousUnitsLocation = {}   # type: Dict[Particle, tuple]
        self.tilesOccupants = {}  # type: Dict[tuple, List[Particle]]
        self.addCustomMoveFunc = None  # type: function

    @property
    @abstractmethod
    def _teamKillAllowed(self) -> bool:
        return False

    @property
    @abstractmethod
    def _suicideAllowed(self) -> bool:
        return False

    def _addCustomMove(self, unit: MovingUnit, move: Path) -> None:
        """
        Uses the "addCustomMoveFunc" that could have been defined by the mainloop to add a move that will be performed
         step by step each frame.

        Args:
            unit: The unit to move
            move: The move for the given unit to perform
        """
        if self.addCustomMoveFunc is not None:
            try:
                self.addCustomMoveFunc(unit, move)
            except TypeError:
                pass

    def addUnit(self, unit: MovingUnit, team_number: int, origin_tile_id: tuple) -> None:
        """
        Adds a unit to the game

        Args:
            unit: The unit to add
            team_number: The number of the team in which the game will put the given unit
            origin_tile_id: The identifier of the tile on which the unit will be placed on
        """
        self._addUnitToTile(origin_tile_id, unit)
        self.players[unit.playerNumber] = unit
        self.unitsTeam[unit] = team_number
        if team_number in self.teams.keys():
            self.teams[team_number].append(unit)
        else:
            self.teams[team_number] = [unit]

    def _addUnitToTile(self, new_tile_id: tuple, unit: Particle) -> None:
        """
        Adds the given unit to the tile for which the id was given.
        Also removes the tile from its previous tile if needed

        Args:
            new_tile_id: The identifier of the tile on which place the given unit
            unit: The unit to place on the given tile.
        """
        try:
            if unit not in self.unitsLocation:
                self.unitsLocation[unit] = new_tile_id  # FIXME need to continue on this
            if unit in self._previousUnitsLocation:
                old_tile_id = self._previousUnitsLocation[unit]
                self.tilesOccupants[old_tile_id].remove(unit)
                if len(self.tilesOccupants[old_tile_id]) == 0:
                    del self.tilesOccupants[old_tile_id]
            self._previousUnitsLocation[unit] = new_tile_id
            if new_tile_id in self.tilesOccupants:
                self.tilesOccupants[new_tile_id].append(unit)
            else:
                self.tilesOccupants[new_tile_id] = [unit]
        except:
            traceback.print_exc()

    def getTileForUnit(self, unit: MovingUnit) -> Tile:
        """
        Args:
            unit: The unit for which the Tile will be given

        Returns: The tile on which the given unit is located
        """
        return self.board.getTileById(self.unitsLocation[unit])

    def isFinished(self) -> bool:
        """
        Returns: True if the game is finished and False otherwise
        """
        return self._finished

    def updateGameState(self, unit: MovingUnit, tile_id: tuple) -> None:
        """
        Change the unit's tile and checks for collisions

        Args:
            unit: The unit that triggered the update
            tile_id: The new tile id on which the unit has been recently placed on.

        Raises:
             InconsistentGameStateException:
                If this method is used illegally (when the unit is not effectively placed on the tile corresponding to
                the given tile_id).
        """
        print("Game update")
        if unit not in self.unitsLocation:
            raise UnknownUnitException("The game is trying to be updated using an unknown unit")
        if tile_id != self.unitsLocation[unit]:
            if unit.isAlive():
                error_msg = "The game is trying to be updated using a unit that is placed on the tile %s instead of %s"\
                                % (str(self.unitsLocation[unit]), str(old_tile_id))
                raise InconsistentGameStateException(error_msg)
            else:
                return
        if self.board.getTileById(tile_id).deadly:
            unit.kill()
            self._removeUnitFromTile(unit, tile_id)
        self._addUnitToTile(tile_id, unit)
        if self._tileHasTwoOrMoreOccupants(tile_id):
            self._handleCollision(unit, self.tilesOccupants[tile_id])
        for unit in self.tilesOccupants[tile_id]:
            if not unit.isAlive():
                self.tilesOccupants[tile_id].remove(unit)
        self._finished = self._checkIfFinished()

    def copy(self):
        return deepcopy(self)

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "addCustomMoveFunc":
                value = deepcopy(v, memo)
            else:
                value = None
            setattr(result, k, value)
        return result

    def belongsToSameTeam(self, unit1: MovingUnit, unit2: MovingUnit):
        """
        Checks if the two given units are in the same team

        Args:
            unit1: The first unit to check
            unit2: The second unit to check

        Returns: True if the two units are in the same team
        """
        if unit1 in self.unitsTeam and unit2 in self.unitsTeam:
            return self.unitsTeam[unit1] == self.unitsTeam[unit2]
        else:
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
                if other_unit in self.unitsLocation.keys():  # If the other unit is a controlled unit
                    self._collidePlayers(unit, other_unit, frontal=True)
                else:  # If the other unit is a Particle
                    other_player = None
                    for player in self.unitsLocation.keys():  # type: MovingUnit
                        if player.hasParticle(other_unit):
                            other_player = player
                            break
                    if other_player is not None:  # If we found the player to which belongs the colliding particle
                        self._collidePlayers(unit, other_player)

    def _checkIfFinished(self) -> bool:
        """
        Checks if there is moe than one team alive.
        If there is, the game is not finished.

        Returns: True if the game is finished, False if the game is not finished
        """
        if self._finished:
            return True
        teams_alive = 0
        team_units = []
        for team in self.teams.values():
            for unit in team:
                if unit.isAlive():
                    teams_alive += 1
                    team_units = team
                    break
        if teams_alive > 1:
            return False
        elif teams_alive == 0:
            self.winningPlayers = ()
            return True
        else:
            self.winningPlayers = tuple(team_units)
            return True

    @abstractmethod
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
        same_team = self.belongsToSameTeam(player1, player2)
        suicide = player1 is player2
        if (not same_team or self._teamKillAllowed) or (suicide and self._suicideAllowed):
            player1.kill()
            if frontal:
                player2.kill()

    @abstractmethod
    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor, max_moves: int=-1, force: bool=False) -> Path:
        """
        Creates a move following the given event coming from the given unit

        Args:
            unit: The unit that triggered the event
            move_descriptor: The descriptor of the move triggered by the given unit
            max_moves: The maximum number of moves done by the move to create (default: -1 => no limitations)
            force: Optional, a bot controller will force the move as it does not need to check if the move is possible

        Returns: A Path of move(s) triggered by the given event for the given unit

        Raises:
            UnfeasibleMoveException: If the move is not possible.
        """
        pass

    def createKeyboardEvent(self, unit: MovingUnit, input_key) -> KeyboardEvent:
        """
        Creates a keyboard event (override for custom events)

        Args:
            unit: The unit that triggered te event
            input_key: The input key pressed on the keyboard

        Returns: The event object to send
        """
        return KeyboardEvent((input_key,))

    def createMouseEvent(self, unit, pixel, mouse_state, click_up, tile_id) -> MouseEvent:
        """
        Creates a mouse event (override for custom events)

        Args:
            unit: The unit that triggered the event
            pixel: The pixel clicked
            mouse_state: The state of the mouse buttons
            click_up: True if the click is "up", False if "down"
            tile_id: The identifier of the tile clicked on (None if no tile was clicked)

        Returns: the event to send
        """
        return MouseEvent(pixel, mouse_state, click_up, tile_id)

    def _tileHasTwoOrMoreOccupants(self, tile_id: tuple) -> bool:
        """

        Args:
            tile_id: The identifier of the tile to test

        Returns: True if the tile has two or more alive occupants
        """
        return len([unit for unit in self.tilesOccupants[tile_id] if unit.isAlive()]) > 1

    def _removeUnitFromTile(self, unit, tile_id):
        old_tile_id = self.unitsLocation[unit]
        del self.unitsLocation[unit]
        self.tilesOccupants[old_tile_id].remove(unit)
        if len(self.tilesOccupants) == 0:
            del self.tilesOccupants[old_tile_id]

