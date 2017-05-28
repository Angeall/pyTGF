from typing import Tuple, Dict, Callable, List

import pandas as pd

from .thoroughroutine import ThoroughRoutine
from ..gatherer import Gatherer
from ...board.simulation.simultaneous_alphabeta import Value, SimultaneousAlphaBeta
from ...characters.moves import MoveDescriptor
from ...controls.controllers import Bot
from ...game import API
from ...game.turnbased import TurnBasedAPI


class BattleBasedRoutine(ThoroughRoutine):
    def __init__(self, opponent_controllers: List[Bot], gatherer: Gatherer, possible_moves: Tuple[MoveDescriptor, ...],
                 eval_fct: Callable[[API], Dict[int, Value]], max_depth: int = -1, must_write_files: bool = True,
                 must_keep_temp_files: bool = False, min_end_states: int = 1, min_victories: int=0):
        super().__init__(gatherer, possible_moves, eval_fct, max_depth, must_write_files, must_keep_temp_files)
        self._bots = {}  # type: Dict[int, Bot]
        for opponent in opponent_controllers:
            opponent.getReady()
            self._bots[opponent.playerNumber] = opponent
        self._minEndStates = min_end_states
        self._minVictories = min_victories

    def routine(self, player_number: int, state: API):
        self._resetValues()
        self._actionsSequences = pd.DataFrame()
        pl_index = state.getPlayerNumbers().index(player_number)
        victories = 0
        last_size = 0
        i = 0
        while self._actionsSequences.shape[0] < len(state.getPlayerNumbers()) * self._minEndStates\
                or victories < self._minVictories:
            super().routine(player_number, state.copy())
            if self._actionsSequences.shape[0] > last_size:
                last_size = self._actionsSequences.shape[0]
                last_rows = list(self._actionsSequences[self._actionsSequences.shape[0] -
                                                        len(state.getPlayerNumbers()):][0])
                if last_rows[pl_index] == 1:
                    victories += 1
            i += 1
            print("games:", i, "victories:", victories)
        return self._actionsSequences

    def _generateMovesList(self, state: API):
        combinations = SimultaneousAlphaBeta._generateMovesList(self, state)
        if not self.turnByTurn:
            return combinations
        assert isinstance(state, TurnBasedAPI)
        order = state.getPlayerNumbersInOrder()
        states = {(): state.copy()}
        past_pl_nums = []
        for i, pl_num in enumerate(order):
            to_keep = []
            if pl_num in self._bots:
                for new_state in states.values():
                    action = self._bots[pl_num]._selectNewMove(new_state)
                    to_keep.extend([comb for comb in combinations if comb[pl_num] == action])
                combinations = [comb for comb in combinations if comb in to_keep]
            past_pl_nums.append(pl_num)
            action_sequences = list(set(state.convertIntoMoveSequence(combinations, max_size=i+1)))
            new_states = {}
            for sequence in action_sequences:
                old_state = states[sequence[:-1]]  # type: TurnBasedAPI
                _succeeded, _state = old_state.simulateMove(past_pl_nums[-1], sequence[-1])
                if _succeeded:
                    new_states[sequence] = _state
                else:
                    print('illagal movement')
            states = new_states
        if not combinations:
            print("Empty combination")
        return combinations