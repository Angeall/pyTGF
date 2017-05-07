from typing import Tuple, Dict, Callable, List

from .battlebasedroutine import BattleBasedRoutine
from ..gatherer import Gatherer
from ...board.simulation.simultaneous_alphabeta import Value
from ...characters.moves import MoveDescriptor
from ...controls.controllers import Bot
from ...game import API


class ReinforcementRoutine(BattleBasedRoutine):
    def __init__(self, own_controller: Bot, opponent_controllers: List[Bot], gatherer: Gatherer,
                 possible_moves: Tuple[MoveDescriptor, ...], eval_fct: Callable[[API], Dict[int, Value]]):
        super().__init__(opponent_controllers, gatherer, possible_moves, eval_fct)
        own_controller.getReady()
        self.opponents[own_controller.playerNumber] = own_controller
