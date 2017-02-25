"""
Contains the definition of a routine to gather daata
"""
import random
from typing import Iterable, Union, Callable, Optional, Tuple, Any, List

import pandas as pd

from pytgf.characters.utils.moves import getMovesCombinations
from pytgf.game import API
from pytgf.learning.component import Data, Component
from pytgf.learning.gatherer import Gatherer

__author__ = "Anthony Rouneau"


class Routine:
    def __init__(self, gatherer: Gatherer, player_number: int, possible_moves: Iterable[Any], max_depth: int=-1):
        self._gatherer = gatherer
        self._playerNumber = player_number
        self._maxDepth = max_depth
        self._possibleMoves = tuple(possible_moves)
        if self._maxDepth == -1:
            self._maxDepth = float('inf')

    def gather(self, api: API, data_frame: pd.DataFrame, depth: int=0):
        # FIXME : Change following the notes => +1 if could win, 0.5 if unfinished, 0 if only lead to loss
        # FIXME :                               +1/nb_turn_to win, or 0 if unfinished or lead to loss
        if api.isFinished():
            if api.hasWon(self._playerNumber):
                return True, 1                                                                                                           # The player has won due to its last move
            else:
                return True, -1  # The player is dead due to its last move
        finished = False
        game_finished_score = 0  # 0 = game not finished
        if depth < self._maxDepth:
            players_moves = {}
            combinations = self._getPlayerMovesCombinations(api, players_moves)
            for combination in combinations:
                succeeded, new_api = api.simulateMoves(combination)
                simulation_finished, simulation_nb_of_turn_until_end = self.gather(new_api, None, depth+1)
                finished = finished or simulation_finished

                # TODO save info in file + return right final score (nb turn before a win ? + lose ?)
        return finished, game_finished_score

    def _getPlayerMovesCombinations(self, api, players_moves):
        for player_number in api.getPlayerNumbers():
            if player_number == self._playerNumber:
                players_moves[player_number] = self._choosePlayerMoves(api)
            else:
                players_moves[player_number] = self._chooseOtherPlayerMoves(api, player_number)
        combinations = getMovesCombinations(players_moves)
        return combinations

    def _choosePlayerMoves(self, api: API) -> List[Any]:
        return api.checkFeasibleMoves(self._playerNumber, self._possibleMoves)

    def _chooseOtherPlayerMoves(self, api: API, other_player_number: int):
        moves = api.checkFeasibleMoves(other_player_number, self._possibleMoves)
        safe_moves = []
        for move in moves:
            if api.isMoveDeadly(other_player_number, move):
                safe_moves.append(move)
        if len(safe_moves) == 0:  # If all the moves are deadly
            safe_moves.append(random.choice(moves))
        return safe_moves



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
