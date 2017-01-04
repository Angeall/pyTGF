from abc import ABCMeta, abstractmethod


class GameState(metaclass=ABCMeta):

    def __init__(self, player_number: tuple, *players_position: tuple):
        self.playerNumber = player_number
        self.enemiesPosition = players_position

    @abstractmethod
    def simulateMove(self, player_number, move):
        pass

    def simulateMoves(self, moves: list):
        for i, move in enumerate(moves):
            if move is not None:
                self.simulateMove(i, move)

