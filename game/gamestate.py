import traceback
from copy import deepcopy

from game.game import Game


class GameState:

    def __init__(self, game: Game):
        self.game = game.copy()

    def simulateMove(self, player_number: int, wanted_move):
        unit = self.game.players[player_number]
        move = self.game.createMoveForEvent(unit, wanted_move, max_moves=1)
        move.complete()

    def simulateMoves(self, player_moves: dict):
        """
        Simulate the given moves for the key players

        Args:
            player_moves: a dictionary with player_numbers as keys and a list of moves for the key player
        """
        for player_number, wanted_move in player_moves.items():
            self.simulateMove(player_number, wanted_move)

