import random
from typing import Tuple, Callable, Union

from ...board.simulation.simultaneous_alphabeta import Value
from ...characters.moves import MoveDescriptor
from ...data.gatherer import Gatherer
from ...data.routines.throughoutroutine import ThroughoutRoutine, MAX_TEMP_VECTORS
from ...game import API

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
        self._lastRandomState = None

    def routine(self, player_number: int, state: API):
        nb_iter = range(self._nbRandomStates)
        res = None
        for _ in nb_iter:
            nb_moves = random.randint(0, self._maxNbSimulatedMoves)
            random_state = self.getRandomState(state.copy(), nb_moves)
            self._prepare(player_number, state)

            if random_state is not None:
                self._lastRandomState = random_state
                self.alphaBetaSearching(player_number, random_state)
                # print(self._actionsSequences)
                res = self._actionsSequences
            if self._totalNbStates >= MAX_TEMP_VECTORS:
                self._writeToFinalFile()
                self._resetValues()
        return res

    def getRandomState(self, state: API, nb_moves: int) -> Union[API, None]:
        """
        Simulate a given number of moves in the given state
        
        Args:
            state: The original state in which simulate the moves 
            nb_moves: The number of moves to simulate

        Returns: Either the resulting API or None if only finished states can be reached
        """
        for player_number in state.getPlayerNumbers():
            if state.game.getUnitForNumber(player_number).lastAction is None:
                state.game.getUnitForNumber(player_number).lastAction = -1
        if state.game.isFinished():
            return None
        elif nb_moves == 0:
            return state
        else:
            new_state = None  # type: API
            moves = {}
            moves_list = self._generateMovesCombinations(state)
            possible_moves = []
            for i in range(len(moves_list)):
                for j in range(len(moves_list[i])):
                    possible_moves.append(moves_list[i][j])

            random.shuffle(possible_moves)
            while len(possible_moves) > 0 and (new_state is None or new_state.isFinished()):
                moves = possible_moves.pop()
                succeeded, new_state = state.simulateMoves(moves)
                if not succeeded:
                    new_state = None
                    continue
                new_state = self.getRandomState(new_state, nb_moves - 1)
            return new_state


