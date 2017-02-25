"""
Contains the definition of a routine to gather daata
"""
import random
from typing import Iterable, Union, Callable, Optional, Tuple, Any, List, Dict

import numpy as np

from pytgf.ai import SimultaneousAlphaBeta
from pytgf.ai.simultaneous_alphabeta import Value, EndState
from pytgf.characters.moves import MoveDescriptor
from pytgf.game import API
from pytgf.learning.component import Data, Component
from pytgf.learning.gatherer import Gatherer

__author__ = "Anthony Rouneau"
ObjID = int


class Routine(SimultaneousAlphaBeta):

    def __init__(self, gatherer: Gatherer, possible_moves: Iterable[Any],
                 eval_fct: Callable[[API], Tuple[Value, ...]], possible_actions: Tuple[MoveDescriptor, ...],
                 max_depth: int = -1):
        super().__init__(eval_fct, possible_actions, max_depth)
        self._gatherer = gatherer
        self._possibleMoves = tuple(possible_moves)
        self._aPrioriDataVectors = {}  # type: Dict[ObjID, np.ndarray]
        self._aPosterioriDataVectors = {}  # type: Dict[ObjID, List[np.ndarray]]
        self._concludedStates = []  # type: List[ObjID]

    def routine(self, player_number: int, state: API):
        self.alphaBetaSearching(player_number, state)
        self._writeToFile()

    def _mustCutOff(self) -> bool:
        """
        Returns: False because our data gathering routine must consider all movements
        """
        return False

    def _maxValue(self, state: API, alpha: float, beta: float, depth: int) \
            -> Tuple[Value, Union[Dict[int, MoveDescriptor], None], EndState, API]:
        self._aPrioriDataVectors[id(state)] = self._gatherer.getAPrioriData(state)
        self._aPosterioriDataVectors[id(state)] = []  # init list for _minValue
        retVal = super()._maxValue(state, alpha, beta, depth)
        self._concludedStates.append(id(state))
        if len(self._concludedStates) > 1000:
            self._writeToTempFile()
        return retVal

    def _minValue(self, state: API, actions: List[Dict[int, MoveDescriptor]], alpha: float, beta: float, depth: int) \
            -> Tuple[Value, Union[Dict[int, MoveDescriptor], None], EndState, API]:
        player_move_descriptor = actions[self.playerNumber]
        value, best_actions, end_state, new_game_state = super()._minValue(state, actions,
                                                                           alpha, beta, depth)  # Simulate the actions
        a_posteriori_data = self._gatherer.getAPosterioriData(state)
        final_state = self._computeFinalStateScore(depth, end_state)
        a_posteriori_data = np.append(player_move_descriptor, a_posteriori_data)
        a_posteriori_data = np.append(a_posteriori_data, final_state)
        self._aPosterioriDataVectors[id(state)].append(a_posteriori_data)
        return value, best_actions, end_state, new_game_state

    @staticmethod
    def _computeFinalStateScore(depth, end_state):
        final_state = (0, 0)  # We suppose that the game has not ended
        if end_state[0]:
            nb_turn = end_state[1] - depth  # The number of turn in which the game ended
            if not end_state[2]:  # If the game ended but the player lost
                final_state = (-1, nb_turn)
            else:
                final_state = (1, nb_turn)
        return final_state

    def _getPossibleMovesForPlayer(self, player_number: int, state: API) -> List[MoveDescriptor]:
        moves = super()._getPossibleMovesForPlayer(player_number, state)
        if player_number == self.playerNumber:
            return moves
        safe_moves = []
        for move in moves:
            if not state.isMoveDeadly(player_number, move):
                safe_moves.append(move)
        if len(safe_moves) == 0:  # If all the moves are deadly
            safe_moves.append(random.choice(moves))
        return safe_moves

    def _writeToTempFile(self):
        # TODO : Convert into DataFrame using self._concludedStates and save it into csv + add name to temp_file_names
        pass

    def _writeToFile(self):
        # TODO : Join temp files of there are and add the last vectors
        pass


class RoutineBuilder:
    """
    Class used to build a Routine
    """
    def __init__(self):
        """
        Instantiates a Routine builder
        """
        self._components = []

    def addComponent(self, methods: Union[Iterable[Callable[[API], Data]], Callable[[API], Data]],
                     reduce_function: Optional[Callable[[Tuple[Data, ...]], Data]]=None) -> None:
        """
        Adds a component to the routine being built

        Args:
            methods: An iterable of methods or just one method that takes an API as a parameter and returns a data
            reduce_function:
                A method that, given a tuple of data, returns a single data (e.g. functools.reduce)
                Unused if the "methods" parameter is a lone method, but necessary if there is more than one method.
        """
        self._components.append(Component(methods, reduce_function))

    def create(self) -> Routine:
        """
        Raises:
            ValueError: If no component was added to this builder, it cannot create a routine, and hence crash

        Returns: The Routine built using this builder
        """
        if len(self._components) == 0:
            raise ValueError("Cannot create a routine with 0 component")
        gatherer = Gatherer(self._components)
        return Routine(gatherer)
