"""
File containing the definition of a basic API to interact with a game from a controller
"""
from abc import ABCMeta, abstractmethod
from typing import Tuple, Dict, Union, List

from pytgf.board import TileIdentifier
from pytgf.characters.moves import IllegalMove, MoveDescriptor
from pytgf.characters.moves import Path
from pytgf.characters.units import MovingUnit
from pytgf.game.core import Core, UnfeasibleMoveException

__author__ = 'Anthony Rouneau'


class API(metaclass=ABCMeta):
    """
    A class defining a basic API so a controller can get information on the current state of the game,
    and simulate new moves in it.
    """
    def __init__(self, game: Core):
        """
        Instantiates the API

        Args:
            game: The game that will be used in this API
        """
        self.game = game

    # -------------------- PUBLIC METHODS -------------------- #

    def simulateMove(self, player_number: int, wanted_move: MoveDescriptor, max_moves: int=1) \
            -> Tuple[bool, Union['API', None]]:
        """
        Simulates the move by creating a new GameState

        Args:
            player_number: The number of the player moving
            wanted_move: The event triggering the move
            max_moves: The maximum number of short moves to perform in case of a path or continuous move.

        Returns:
            A copy of this GameState in which the move have been applied (if it is possible)
        """
        feasible_move, move = self._generateMove(player_number, wanted_move)
        if feasible_move:
            new_game_state = self.copy();
            new_game_state.performMove(player_number, wanted_move, max_moves=max_moves)
            return feasible_move, new_game_state
        else:
            return False, None

    def simulateMoves(self, player_moves: Dict[int, MoveDescriptor], max_moves: int=1) \
            -> Tuple[bool, Union['API', None]]:
        """
        Simulates the given moves for the key players

        Args:
            player_moves: a dictionary with player_number as key and a move as value for the key player
            max_moves: The maximum number of short moves to perform in case of a path or continuous move.

        Returns:
            - A boolean -- True if all the moves succeeded, False otherwise
            - A copy of this GameState in which the moves have been applied (if a move is unfeasible, returns None).
        """
        moves = []
        for player_number, wanted_move in player_moves.items():
            feasible_move, move = self._generateMove(player_number, wanted_move)
            if not feasible_move:
                print(self.getPlayerLocation(player_number), self.getCurrentDirection(player_number), wanted_move)
                return False, None
            moves.append(move)
        new_game_state = self.copy()
        for player_number, wanted_move in player_moves.items():
            new_game_state.performMove(player_number, wanted_move, max_moves=max_moves)
        return True, new_game_state

    def performMove(self, player_number: int, move_descriptor: MoveDescriptor, force: bool=False, max_moves: int=1) \
            -> bool:
        """
        Performs the move inside this GameState

        Args:
            player_number: The number of the player moving
            move_descriptor: The move to perform (either a Path or a move descriptor)
            force: Boolean that indicates if the move must be forced into the game (is optional in the game def...)
            max_moves: The maximum number of short moves to perform in case of a path or continuous move.
        """
        unit = self.game.getUnitForNumber(player_number) # type: MovingUnit
        try:
            move = self.createMoveForDescriptor(unit, move_descriptor, max_moves=max_moves, force=force)
            new_tile_id = move.complete()
            unit.currentAction = move_descriptor
            self.game.updateGameState(unit, new_tile_id)
        except UnfeasibleMoveException:
            return False
        except IllegalMove:
            unit.kill()
        return True

    def belongsToSameTeam(self, player_1_number: int, player_2_number: int) -> bool:
        """
        Checks if two players are in the same team

        Args:
            player_1_number: The number representing the first player to check
            player_2_number: The number representing the second player to check

        Returns: True if the two players belongs to the same team, False otherwise.
        """
        return self.game.belongsToSameTeam(self.game.players[player_1_number], self.game.players[player_2_number])

    def getPlayerNumbers(self):
        """
        Returns: The list of the number of each player, sorted !
        """
        players = list(self.game.players.keys())
        players.sort()
        return players

    def getNumberOfTeams(self) -> int:
        """
        Returns: The number of teams playing the game
        """
        return len(self.game.teams)

    def getNumberOfAlivePlayers(self) -> int:
        """
        Returns: The number of alive player in the game
        """
        alive_units = 0
        for unit in self.game.players.values():
            if unit.isAlive():
                alive_units += 1
        return alive_units

    def checkFeasibleMoves(self, player_number: int, possible_moves: Tuple[MoveDescriptor, ...]) -> \
            List[MoveDescriptor]:
        """
        Keeps only the feasible moves in the given list of possible moves

        Args:
            player_number: The number of the player that wants to know its possible moves
            possible_moves: The total list of possible moves, that will be filtered to keep only the feasible ones

        Returns: The list of all the feasible moves among the possible ones
        """
        if not self.game.players[player_number].isAlive():  # If the unit is dead, no move is feasible for it
            return []
        feasible_moves = []
        for move in possible_moves:
            if self._generateMove(player_number, move)[0]:
                feasible_moves.append(move)
        return feasible_moves

    def isFinished(self) -> bool:
        """
        Returns: True if the game is in a final state
        """
        self.game.checkIfFinished()
        return self.game.isFinished()

    def isPlayerAlive(self, player_number: int) -> bool:
        """

        Args:
            player_number: The number of the player for which we want to know the state.

        Returns: True if the player is alive, False otherwise
        """
        return self.game.players[player_number].isAlive()

    def hasWon(self, player_number: int) -> bool:
        """

        Args:
            player_number: The number representing the player.

        Returns: True if the player represented by the given number has won.
        """
        unit = self.game.getUnitForNumber(player_number)
        return self.isFinished() and unit in self.game.winningPlayers

    def getPlayerLocation(self, player_number: int) -> TileIdentifier:
        """

        Args:
            player_number: The number of the player for which we want to know the state.

        Returns: The (i, j) coordinates of the player, i being the row index and j being the column index.
        """
        return self.game.unitsLocation[self.game.players[player_number]]

    def getAdjacent(self, tile_id: TileIdentifier) -> Tuple[TileIdentifier, ...]:
        """

        Args:
            tile_id:
                The (i, j) coordinates of the tile for which we want the adjacent tiles,
                i being the row index and j being the column index.

        Returns: A tuple containing each identifier of the tiles adjacent to the tile for which the id was given
        """
        return self.game.board.getNeighboursIdentifier(tile_id)

    def isMoveDeadly(self, player_number: int, move_descriptor: MoveDescriptor, max_moves: int=1) -> bool:
        """

        Args:
            player_number: The player that will perform the move
            move_descriptor: The descriptor of the move to perform
            max_moves: The maximum number of short moves performed during the simulation (used for continuous moves)

        Returns: True if the move kills the unit in the simulation
        """
        if self.isPlayerAlive(player_number):
            succeeded, new_api = self.simulateMove(player_number, move_descriptor, max_moves)
            if succeeded:
                return not new_api.isPlayerAlive(player_number)
        return True

    def copy(self):
        return type(self)(self.game.copy())

    @abstractmethod
    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor: MoveDescriptor, max_moves: int=-1,
                                force: bool=False) -> Path:
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

    # -------------------- PROTECTED METHODS -------------------- #

    def _generateMove(self, player_number: int, wanted_move: MoveDescriptor) -> Tuple[bool, Union[Path, None]]:
        """
        Generates a move for a given event

        Args:
            player_number: The player that must perform the move
            wanted_move: The descriptor of the move to perform

        Returns:
            A tuple containing

             - A bool set to True if the move was successfully created, set to False otherwise
             - The Path created from the given move descriptor, or None if the move was not successfully created

        """
        unit = self.game.players[player_number]
        try:
            move = self.createMoveForDescriptor(unit, wanted_move, max_moves=1)
            return True, move
        except UnfeasibleMoveException:
            return False, None
