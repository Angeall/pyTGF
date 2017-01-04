from abc import ABCMeta, abstractmethod
from types import FunctionType as function

from board.board import Board
from board.tile import Tile
from characters.moves.path import Path
from characters.units.unit import Unit


class InconsistentGameStateException(Exception):
    pass


class UnknownUnitException(Exception):
    pass


class UnfeasibleMoveException(Exception):
    pass


class Game(metaclass=ABCMeta):
    # TODO: add simulation capabilities. Careful to the units occupant update !
    def __init__(self, board: Board):
        self.board = board
        self._teamKill = False
        self._suicide = False
        self._finished = False
        self.winningPlayers = None
        # self._teams -> keys: int; values: units
        self.teams = {}
        # self._units -> keys: Units; values: tile_ids
        self.units = {}
        self.addCustomMoveFunc = None  # type: function

    def _addCustomMove(self, unit: Unit, move: Path):
        if self.addCustomMoveFunc is not None:
            try:
                self.addCustomMoveFunc(unit, move)
            except TypeError:
                pass

    def addUnit(self, unit: Unit, origin_tile_id: tuple) -> None:
        """
        Adds a unit to the game
        Args:
            unit: The unit to add
            origin_tile_id: The identifier of the tile on which the unit will be placed on
        """
        self.units[unit] = origin_tile_id

    def addToTeam(self, team_number, unit) -> None:
        """
        Adds a unit to the given team
        Args:
            team_number: The number of the team to which add the unit
            unit: The unit to add to the given team number
        """
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
        return self.board.getTileById(self.units[unit])

    def isFinished(self) -> bool:
        """
        Returns: True if the game is finished and False otherwise
        """
        return self._finished

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

    def updateGameState(self, unit: Unit, tile_id: tuple) -> None:
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
        if unit not in self.board.getTileById(tile_id):
            if unit not in self.units:
                raise UnknownUnitException("The game is trying to be updated using an unknown unit")
            else:
                error_msg = "The game is trying to be updated using a unit that is placed on the tile %s instead of %s"\
                                % (self.units[unit].identifier, tile_id)
                raise InconsistentGameStateException(error_msg)
        self.units[unit] = tile_id
        new_tile = self.board.getTileById(tile_id)
        if new_tile.hasTwoOrMoreOccupants():
            self._handleCollision(unit, new_tile.occupants)
        self._finished = self._checkIfFinished()

    def _fromSameTeam(self, unit1, unit2):
        """
        Checks if the two given units are in the same team
        Args:
            unit1: The first unit to check
            unit2: The second unit to check

        Returns: True if the two units are in the same team
        """
        for team in self.teams.keys():
            team_units = self.teams[team]
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
                if other_unit in self.units.keys():  # If the other unit is a controlled unit
                    self._collidePlayers(unit, other_unit, frontal=True)
                else:  # If the other unit is a Particle
                    other_player = None
                    for player in self.units.keys():  # type: Unit
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

    @abstractmethod
    def createMoveForEvent(self, unit: Unit, event) -> Path:
        """
        Creates a move following the given event coming from the given unit

        Args:
            unit: The unit that triggered the event
            event: The event triggered by the given unit and that will generate the move

        Returns: A Path of move(s) triggered by the given event for the given unit

        Raises:
            UnfeasibleMoveException: If the move is not possible.
        """
        pass
