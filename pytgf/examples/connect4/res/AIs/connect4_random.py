import random

from pytgf.examples.connect4.controllers import Connect4BotPlayer
from pytgf.examples.connect4.rules import Connect4API


class Connect4Random(Connect4BotPlayer):
    def _selectNewMove(self, game_state: Connect4API):
        winning_move = game_state.getDirectWinningMove(self.playerNumber)
        if winning_move is not None:
            return winning_move
        losing_move = game_state.getDirectLosingMove(self.playerNumber)
        if losing_move is not None:
            return losing_move  # Block the opponent
        succeeded = False
        move = random.choice(self.possibleMoves)
        while not succeeded:
            move = random.choice(self.possibleMoves)
            succeeded, _ = self.gameState.simulateMove(self.playerNumber, move)
        return move
