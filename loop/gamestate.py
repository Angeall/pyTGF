from abc import ABCMeta, abstractmethod

from loop.game import Game


class GameState(metaclass=ABCMeta):

    def __init__(self, game: Game):
        self.game = game.copy()

    def simulateMove(self, player_number, move):
        unit = self.game.players[player_number]

    def simulateMoves(self, moves: list):
        for i, move in enumerate(moves):
            if move is not None:
                self.simulateMove(i, move)

