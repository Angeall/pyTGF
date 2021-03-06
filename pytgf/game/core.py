"""
File containing the definition of a Game.
"""

from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Dict, List, Union, Tuple, Callable, Optional

from ..board import Board, Tile
from ..board import TileIdentifier
from ..characters.moves import MoveDescriptor
from ..characters.moves import Path
from ..characters.units import Entity
from ..characters.units import Unit
from ..characters.utils.units import resize_unit
from ..controls.events import KeyboardEvent, MouseEvent
from ..utils.geom import Coordinates

__author__ = 'Anthony Rouneau'


class InconsistentGameStateException(Exception):
    """
    Exception raised when the game state is updated, and the unit is not placed on the correct tile
    """
    pass


class UnknownUnitException(Exception):
    """
    Exception raised when an unknown unit is trying to be updated in the game
    """
    pass


class UnfeasibleMoveException(Exception):
    """
    Exception raised when a new move is trying to be created, but is not feasible for the current game state
    """
    pass


class Core(metaclass=ABCMeta):
    """
    The Game contains a Board, containing Tiles, but also Units, placed on Tiles
    """
    def __init__(self, board: Board):
        """
        Creates a new Game using the given board

        Args:
            board:
                The board, containing the needed Tiles that will be used for the game.
                The units are added later on the board.
        """
        self.board = board  # type: Board
        self._finished = False
        self.playerNumbers = []  # type: List[int]

        self.winningPlayers = None
        self.winningTeam = None
        self.teams = {}  # type: Dict[int, List[Unit]]
        self.unitsTeam = {}  # type: Dict[Unit, int]
        self.units = {}  # type: Dict[int, Unit]
        self.avatars = {}  # type: Dict[int, Unit]
        self.controlledBy = {}  # type: Dict[int, int]
        self._activeUnits = {}  # type: Dict[int, Unit]
        self.unitsLocation = {}   # type: Dict[Entity, tuple]
        self._previousUnitsLocation = {}   # type: Dict[Entity, tuple]
        self.tilesOccupants = {}  # type: Dict[tuple, List[Entity]]
        self.addCustomMoveFunc = None  # type: Callable[[Entity, Path, MoveDescriptor], None]

    # -------------------- PUBLIC METHODS -------------------- #

    def addUnit(self, unit: Entity, team_number: int, origin_tile_id: TileIdentifier,
                is_avatar: bool=True, active: bool=True, controlled_by: int=None) -> None:
        """
        Adds a unit to the game

        Args:
            controlled_by: 
                The number of the player that controls this unit. Has sense only if it is an "non-controlled" unit 
                (optional)
            unit: The unit to add
            team_number: The number of the team in which the game will put the given unit
            origin_tile_id: The identifier of the tile on which the unit will be placed on
            is_avatar: True if this unit is controlled by a bot or a human, and hence, is his avatar in the game
            active: True if this unit must count in the "checkIfFinished" method. False if it must not count...
        """
        self.addUnitToTile(origin_tile_id, unit)
        self.units[unit.playerNumber] = unit
        if is_avatar:
            self.avatars[unit.playerNumber] = unit
            self.playerNumbers.append(unit.playerNumber)
            self.controlledBy[unit.playerNumber] = unit.playerNumber
        elif controlled_by is not None:
            self.controlledBy[unit.playerNumber] = controlled_by
        if active:
            self._activeUnits[unit.playerNumber] = unit
        self.unitsTeam[unit] = team_number
        resize_unit(unit, self.board)
        if team_number in self.teams.keys():
            self.teams[team_number].append(unit)
        else:
            self.teams[team_number] = [unit]

    def getTileForUnit(self, unit: Unit) -> Tile:
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

    def updateGameState(self, unit: Unit, tile_id: TileIdentifier, move_descriptor: MoveDescriptor) -> None:
        """
        Change the unit's tile and checks for collisions

        Args:
            unit: The unit that triggered the update
            tile_id: The new tile id on which the unit has been recently placed on.
            move_descriptor: The descriptor of the move that led to this update

        Raises:
             InconsistentGameStateException:
                If this method is used illegally (when the unit is not effectively placed on the tile corresponding to
                the given tile_id).
        """
        if not self._finished:
            if unit not in self.unitsLocation:
                raise UnknownUnitException("The game is trying to be updated using an unknown unit")
            if tile_id != self.unitsLocation[unit]:
                if unit.isAlive():
                    error_msg = "The game is being updated using a unit that is placed on the tile %s instead of %s"\
                                    % (str(self.unitsLocation[unit]), str(tile_id))
                    raise InconsistentGameStateException(error_msg)
                else:
                    return
            unit.lastAction = move_descriptor
            self.addUnitToTile(tile_id, unit)
            if self.board.getTileById(tile_id).deadly:
                unit.kill()
                self._removeUnitFromTile(unit)
            else:
                if self._tileHasTwoOrMoreOccupants(tile_id):
                    self._handleCollision(unit, self.tilesOccupants[tile_id], tile_id)
                for unit in self.tilesOccupants[tile_id]:
                    if not unit.isAlive():
                        self.tilesOccupants[tile_id].remove(unit)

    def copy(self) -> 'Core':
        """
        Copy this game so that any modification on the copy does not affect this one.

        Returns: A deep copy of the game
        """
        return deepcopy(self)

    def belongsToSameTeam(self, unit1: Unit, unit2: Unit) -> bool:
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

    def checkIfFinished(self) -> bool:
        """
        Checks if there is moe than one team alive.
        If there is, the game is not finished.

        Returns: True if the game is finished, False if the game is not finished
        """
        if self._finished:
            return True
        teams_alive = 0
        team_units = []
        winning_team = None
        for team_number, team_players in self.teams.items():
            for unit in team_players:
                if unit.isAlive() and unit.playerNumber in self._activeUnits:
                    teams_alive += 1
                    team_units = team_players
                    winning_team = team_number
                    break
        if teams_alive > 1:
            return False
        else:
            self._finished = True
            if teams_alive == 0:
                self.winningPlayers = ()
                self.winningTeam = None
            else:
                self.winningPlayers = tuple([unit for unit in team_units if unit.playerNumber
                                             in self.avatars])
                self.winningTeam = winning_team
            return True

    def createKeyboardEvent(self, unit: Unit, input_key) -> KeyboardEvent:
        """
        Creates a keyboard event (override for custom events)

        Args:
            unit: The unit that triggered te event
            input_key: The input key pressed on the keyboard

        Returns: The event object to send
        """
        return KeyboardEvent((input_key,))

    def createMouseEvent(self, unit: Unit, pixel: Coordinates, mouse_state: Tuple[bool, bool, bool],
                         click_up: bool, tile_id: TileIdentifier) -> MouseEvent:
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

    def getUnitForNumber(self, player_number: int) -> Unit:
        """
        Args:
            player_number: The number representing the wanted unit

        Returns: The unit linked to the given number
        """
        return self.units[player_number]

    def getControllerUnitForNumber(self, player_number: int) -> Union[Unit, None]:
        """
        Args:
            player_number: The number representing the wanted unit

        Returns: 
            The controlled unit linked to the given number, or None if there is no controlled unit behind the number 
        """
        try:
            return self.avatars[self.controlledBy[player_number]]
        except KeyError:
            return None

    def getTileIdForUnit(self, unit: Entity) -> Union[tuple, None]:
        """

        Args:
            unit: The unit for which we want the tile ID

        Returns: The identifier of the tile on which the unit is placed on, None if it's dead or not located on any tile
        """
        if unit in self.unitsLocation:
            return self.unitsLocation[unit]

    def getTileOccupants(self, tile_id: TileIdentifier) -> Tuple[Entity, ...]:
        """

        Args:
            tile_id: The identifier of the tile, of which we want the occupants

        Returns: A tuple containing all the occupants of this tile, or None if there is none
        """
        if tile_id in self.tilesOccupants:
            return tuple(self.tilesOccupants[tile_id])
        return ()

    def addCustomMove(self, unit: Unit, move: Path, event: MoveDescriptor) -> None:
        """
        Uses the "addCustomMoveFunc" that could have been defined by the mainloop to add a move that will be performed
         step by step each frame.

        Args:
            unit: The unit to move
            move: The move for the given unit to perform
            event: The descriptor of the move to create
        """
        if self.addCustomMoveFunc is not None:
            try:
                self.addCustomMoveFunc(unit, move, event)
            except TypeError:
                pass

    def addUnitToTile(self, new_tile_id: TileIdentifier, unit: Entity) -> None:
        """
        Adds the given unit to the tile for which the id was given.
        Also removes the tile from its previous tile if needed

        Args:
            new_tile_id: The identifier of the tile on which place the given unit
            unit: The unit to place on the given tile.
        """
        if unit not in self.unitsLocation:
            self.unitsLocation[unit] = new_tile_id
        if unit in self._previousUnitsLocation:
            old_tile_id = self._previousUnitsLocation[unit]
            if unit in self.tilesOccupants[old_tile_id]:
                self.tilesOccupants[old_tile_id].remove(unit)
            if len(self.tilesOccupants[old_tile_id]) == 0:
                del self.tilesOccupants[old_tile_id]
        self._previousUnitsLocation[unit] = new_tile_id
        if new_tile_id in self.tilesOccupants:
            self.tilesOccupants[new_tile_id].append(unit)
        else:
            self.tilesOccupants[new_tile_id] = [unit]

    # -------------------- PROTECTED METHODS -------------------- #

    def _handleCollision(self, unit: Unit, entities: List[Entity], tile_id: TileIdentifier) -> None:
        """
        Handles a collision between a unit and other units

        Args:
            unit: The moving unit
            entity: The other units that are on the same tile than the moving unit
        """
        for entity in entities:
            if not (unit is entity):
                if entity not in self.unitsLocation.keys():  # If the other unit is an Entity
                    other_player = None
                    for player in self.unitsLocation.keys():  # type: Unit
                        if player.hasentity(entity):
                            other_player = player
                            break
                    if other_player is not None:  # If we found the player to which belongs the colliding entity
                        self._collidePlayers(unit, other_player, tile_id, entity=entity)
                else:
                    self._collidePlayers(unit, entity, tile_id, frontal=True)

    def _tileHasTwoOrMoreOccupants(self, tile_id: TileIdentifier) -> bool:
        """

        Args:
            tile_id: The identifier of the tile to test

        Returns: True if the tile has two or more alive occupants
        """
        return len([unit for unit in self.tilesOccupants[tile_id] if unit.isAlive()]) > 1

    def _removeUnitFromTile(self, unit: Unit) -> None:
        """
        Removes the given unit from its current tile

        Args:
            unit: The unit to remove
        """
        old_tile_id = self.unitsLocation[unit]
        del self.unitsLocation[unit]
        self.tilesOccupants[old_tile_id].remove(unit)
        if len(self.tilesOccupants) == 0:
            del self.tilesOccupants[old_tile_id]

    @property
    @abstractmethod
    def _teamKillAllowed(self) -> bool:
        """
        Returns: True if the team kill is allowed (i.e. A player on of its entity can kill his teammates)
        """
        return False

    @property
    @abstractmethod
    def _suicideAllowed(self) -> bool:
        """
        Returns: True if a unit can kill itself with one of its entities.
        """
        return False

    @abstractmethod
    def _collidePlayers(self, player1: Unit, player2: Union[Unit, Entity], tile_id: TileIdentifier,
                        frontal: bool = False, entity: Optional[Entity]=None):
        """
        Makes what it has to be done when the first given player collides with an entity of the second given player
        (Careful : two moving units (alive units) colliding each other causes a frontal collision that hurts both
        units)

        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
            tile_id: The identifier of the tile on which the collision took place.
            entity:
                The entity (belonging to player 2) which caused the collision.
                Can be None is no entity caused the collision
        """
        same_team = self.belongsToSameTeam(player1, player2)
        suicide = player1 is player2
        if (not same_team or self._teamKillAllowed) or (suicide and self._suicideAllowed):
            player1.kill()
            if frontal:
                player2.kill()

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
