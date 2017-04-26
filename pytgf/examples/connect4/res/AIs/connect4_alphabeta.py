from abc import ABCMeta, abstractmethod
from typing import Dict

from pytgf.board.simulation import SimultaneousAlphaBeta
from pytgf.characters.moves import MoveDescriptor
from pytgf.examples.connect4.controllers.player import Connect4BotPlayer
from pytgf.examples.connect4.rules import Connect4API


def eval_fct(game_state: Connect4API) -> Dict[int, float]:
    scores = {}
    for player_number in game_state.getPlayerNumbers():
        score = 0
        if game_state.hasWon(player_number):
            score = 1000
        elif not game_state.isPlayerAlive(player_number):
            score = -1000
        scores[player_number] = score
    return scores


class Connect4AlphaBeta(Connect4BotPlayer, metaclass=ABCMeta):
    def __init__(self, player_number: int):
        super().__init__(player_number)
        self._alphaBeta = SimultaneousAlphaBeta(self.evalFct, self.possibleMoves, max_depth=self._maxDepth)
        print("Created")

    def _selectNewMove(self, game_state: Connect4API) -> MoveDescriptor:
        value = self._alphaBeta.alphaBetaSearching(self.playerNumber, game_state)
        return value

    @staticmethod
    def evalFct(game_state: Connect4API) -> Dict[int, float]:
        return eval_fct(game_state)

    @property
    @abstractmethod
    def _maxDepth(self) -> int:
        pass
