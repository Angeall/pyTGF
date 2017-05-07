from typing import Tuple, Dict, Callable, List

from .thoroughroutine import ThoroughRoutine
from ..gatherer import Gatherer
from ...board.simulation.simultaneous_alphabeta import Value
from ...characters.moves import MoveDescriptor
from ...controls.controllers import Bot
from ...game import API


class BattleBasedRoutine(ThoroughRoutine):
    def __init__(self, opponent_controllers: List[Bot], gatherer: Gatherer, possible_moves: Tuple[MoveDescriptor, ...],
                 eval_fct: Callable[[API], Dict[int, Value]]):
        super().__init__(gatherer, possible_moves, eval_fct)
        self.opponents = {}
        for opponent in opponent_controllers:
            opponent.getReady()
            self.opponents[opponent.playerNumber] = opponent

    def _getPossibleMovesForPlayer(self, player_number: int, state: API) -> List[MoveDescriptor]:
        if player_number in self.opponents:
            controller = self.opponents[player_number]  # type: Bot
            action = controller._selectNewMove(state)
            return [action]
        else:
            return super()._getPossibleMovesForPlayer(player_number, state)
