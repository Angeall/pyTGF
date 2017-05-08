from typing import Tuple, Dict, Callable, List

from .battlebasedroutine import BattleBasedRoutine
from ..gatherer import Gatherer
from ...board.simulation.simultaneous_alphabeta import Value
from ...characters.moves import MoveDescriptor
from ...controls.controllers import Bot
from ...game import API


class ReinforcementRoutine(BattleBasedRoutine):
    def __init__(self, own_controller: Bot, opponent_controllers: List[Bot], gatherer: Gatherer,
                 possible_moves: Tuple[MoveDescriptor, ...], eval_fct: Callable[[API], Dict[int, Value]],
                 max_depth: int = -1, must_write_files: bool = True, must_keep_temp_files: bool = False,
                 min_end_states: int=1, min_victories: int=0):
        super().__init__(opponent_controllers, gatherer, possible_moves, eval_fct, max_depth, must_write_files,
                         must_keep_temp_files, min_end_states, min_victories)
        own_controller.getReady()
        self._bots[own_controller.playerNumber] = own_controller
