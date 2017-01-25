import traceback
from typing import Union, Any, Tuple

from characters.moves.move import IllegalMove, ImpossibleMove
from characters.moves.path import Path
from characters.units.moving_unit import MovingUnit
from game.game import Game, UnfeasibleMoveException

direction_str = ["RIGHT", "UP", "LEFT", "DOWN"]


class GameState:

    def __init__(self, game: Game):
        self.game = game

    def simulateMove(self, player_number: int, wanted_move) -> tuple:
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

    def simulateMoves(self, player_moves: dict) -> tuple:
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

    def performMove(self, player_number: int, move_descriptor, force: bool=False) -> bool:
        """
        Performs the move inside this GameState

        Args:
            player_number: The number of the player moving
            move_descriptor: The move to perform (either a Path or a move descriptor)
            force: Boolean that indicates if the move must be forced into the game (is optional in the game def...)
        """
        try:
            unit = self.game.players[player_number]  # type: MovingUnit
            move = self.game.createMoveForDescriptor(unit, move_descriptor, max_moves=1, force=force)
            new_tile_id = move.complete()
            unit.currentAction = move_descriptor
            self.game.updateGameState(unit, new_tile_id)
        except UnfeasibleMoveException:
            return False
        except IllegalMove:
            print("Illegal move for player", player_number, "for gamestate", self)
            self.game.players[player_number].kill()
        finally:
            return True

    def belongsToSameTeam(self, player_1_number: int, player_2_number: int) -> bool:
        return self.game.belongsToSameTeam(self.game.players[player_1_number], self.game.players[player_2_number])

    def getPlayerNumbers(self):
        """
        Returns: The list of the number of each player, sorted !
        """
        players = list(self.game.players.keys())
        players.sort()
        return players

    def getNumberOfTeams(self):
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

    def checkFeasibleMoves(self, player_number: int, possible_moves: tuple) -> list:
        """
        Keeps only the feasible moves in the given list of possible moves

        Args:
            player_number: The number of the player that wants to know its possible moves
            possible_moves: The total list of possible moves, that will be filtered to keep only the feasible ones

        Returns: The list of all the feasible moves among the possible ones
        """
        if not self.game.players[player_number].isAlive():  # If the unit is dead, no move is feasible for it
            print('player', player_number, "is dead in gamestate", self)
            return []
        feasible_moves = []
        for move in possible_moves:
            if self._generateMove(player_number, move)[0]:
                feasible_moves.append(move)
        return feasible_moves

    def isFinished(self) ->bool:
        """
        Returns: True if the game is in a final state
        """
        return self.game.isFinished()

    def _generateMove(self, player_number: int, wanted_move) -> tuple:
        """
        Generates a move for a given event

        Args:
            player_number: The player that must perform the move
            wanted_move: The move

        Returns:

        """
        unit = self.game.players[player_number]
        try:
            move = self.game.createMoveForDescriptor(unit, wanted_move, max_moves=1)
            return True, move
        except UnfeasibleMoveException:
            return False, None
