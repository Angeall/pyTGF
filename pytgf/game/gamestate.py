"""
File containing the definition of a basic API to interact with a game from a controller
"""

from typing import Tuple, Dict, Union, List

from pytgf.board import TileIdentifier
from pytgf.characters.moves import IllegalMove, MoveDescriptor
from pytgf.characters.moves import Path
from pytgf.characters.units import MovingUnit
from pytgf.game import Game, UnfeasibleMoveException

__author__ = 'Anthony Rouneau'


class GameState:
    """
    A class defining a basic API so a controller can get information on the current state of the game,
    and simulate new moves in it.
    """
    def __init__(self, game: Game):
        """
        Instantiates the API

        Args:
            game: The game that will be used in this API
        """
        self.game = game

    # -------------------- PUBLIC METHODS -------------------- #

    def simulateMove(self, player_number: int, wanted_move: MoveDescriptor) -> Tuple[bool, Union['GameState', None]]:
        """
        Simulates the move by creating a new GameState

        Args:
            player_number: The number of the player moving
            wanted_move: The event triggering the move

        Returns:
            A copy of this GameState in which the move have been applied (if it is possible)
        """
        feasible_move, move = self._generateMove(player_number, wanted_move)
        if feasible_move:
            new_game_state = GameState(self.game.copy())
            new_game_state.performMove(player_number, wanted_move)
            return feasible_move, new_game_state
        else:
            return False, None

    def simulateMoves(self, player_moves: Dict[int, MoveDescriptor]) -> Tuple[bool, Union['GameState', None]]:
        """
        Simulates the given moves for the key players

        Args:
            player_moves: a dictionary with player_number as key and a move as value for the key player

        Returns:
            - A boolean -- True if all the moves succeeded, False otherwise
            - A copy of this GameState in which the moves have been applied (if a move is unfeasible, returns None).
        """
        moves = []
        for player_number, wanted_move in player_moves.items():
            feasible_move, move = self._generateMove(player_number, wanted_move)
            if not feasible_move:
                return False, None
            moves.append(move)
        new_game_state = GameState(self.game.copy())
        for player_number, wanted_move in player_moves.items():
            new_game_state.performMove(player_number, wanted_move)
        return True, new_game_state

    def performMove(self, player_number: int, move_descriptor: MoveDescriptor, force: bool=False) -> bool:
        """
        Performs the move inside this GameState

        Args:
            player_number: The number of the player moving
            move_descriptor: The move to perform (either a Path or a move descriptor)
            force: Boolean that indicates if the move must be forced into the game (is optional in the game def...)
        """
        unit = self.game.players[player_number]  # type: MovingUnit
        try:
            move = self.game.createMoveForDescriptor(unit, move_descriptor, max_moves=1, force=force)
            new_tile_id = move.complete()
            unit.currentAction = move_descriptor
            self.game.updateGameState(unit, new_tile_id)
        except UnfeasibleMoveException:
            return False
        except IllegalMove:
            unit.kill()
        finally:
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
            player_number: The number of the player for which we want to know its state.

        Returns: True if the player is alive, False otherwise
        """
        return self.game.players[player_number].isAlive()

    def getPlayerLocation(self, player_number: int) -> TileIdentifier:
        """

        Args:
            player_number: The number of the player for which we want to know its state.

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
            move = self.game.createMoveForDescriptor(unit, wanted_move, max_moves=1)
            return True, move
        except UnfeasibleMoveException:
            return False, None
