import random

from typing import Tuple, Callable, Union

from pytgf.ai.simultaneous_alphabeta import Value
from pytgf.characters.moves import MoveDescriptor
from pytgf.data.gatherer import Gatherer
from pytgf.data.throughoutroutine import ThroughoutRoutine
from pytgf.game import API

__author__ = "Anthony Rouneau"


class RandomRoutine(ThroughoutRoutine):

    def __init__(self, gatherer: Gatherer, possible_moves: Tuple[MoveDescriptor, ...],
                 eval_fct: Callable[[API], Tuple[Value, ...]], nb_random_states: int, max_nb_simulated_moves: int,
                 max_depth: int = -1, must_write_files: bool=True, must_keep_temp_files: bool=False,
                 max_end_states: int=-1, max_step_per_moves: int=-1):
        super().__init__(gatherer, possible_moves, eval_fct, max_depth, must_write_files, must_keep_temp_files,
                         max_end_states)
        self._nbRandomStates = nb_random_states
        self._maxNbSimulatedMoves = max_nb_simulated_moves
        self._maxStepPerMoves = max_step_per_moves

    def routine(self, player_number: int, state: API):
        self._prepare(player_number, state)
        for _ in range(self._nbRandomStates):
            nb_moves = random.randint(0, self._maxNbSimulatedMoves)
            print(nb_moves)
            random_state = self.simulateMoves(state, nb_moves,
                                              self._maxStepPerMoves)
            super().routine(player_number, random_state)

    def simulateMoves(self, state: API, nb_moves: int, max_moves_per_step: int=-1) -> Union[API, None]:
        """
        Simulate a given number of moves in the given state
        
        Args:
            state: The original state in which simulate the moves 
            nb_moves: The number of moves to simulate
            max_moves_per_step: The maximum number of short moves to perform at each step (-1 = infinite)

        Returns: Either the resulting API or None if only finished states can be reached
        """
        if state.isFinished():
            self._deleteLastActions()
            return None
        elif nb_moves == 0:
            return state
        else:
            new_state = None  # API
            moves = {}
            while new_state is None or new_state.isFinished():
                possible_moves = self._generateMovesCombinations(state)
                moves = random.choice(random.choice(possible_moves))
                succeeded, new_state = state.simulateMoves(moves, max_moves_per_step)
                if not succeeded:
                    new_state = None
                    continue
                new_state = self.simulateMoves(new_state, nb_moves-1, max_moves_per_step)
            self._registerCurrentActions(moves, state)
            for player_number, action in moves.items():
                new_state.game.getUnitForNumber(player_number).lastAction = action
            return new_state


