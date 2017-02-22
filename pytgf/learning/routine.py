"""
Contains the definition of a routine to gather daata
"""
from typing import Iterable, Union, Callable, Optional, Tuple, Any, List

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

    def gather(self, api: API, depth: int=0):
        if api.isFinished():
            return int(api.isPlayerAlive(self._playerNumber))  # If the player is alive at the end of the game, it won
        finished = False
        if depth < self._maxDepth:
            players_moves = {}
            for player_number in api.getPlayerNumbers():
                if player_number == self._playerNumber:
                    players_moves[player_number] = self._choosePlayerMoves(api)
                else:
                    players_moves[player_number] = self._chooseOtherPlayerMoves(api, player_number)
            combinations = getMovesCombinations(players_moves)
            for combination in combinations:
                succeeded, new_api = api.simulateMoves(combination)
                finished = finished or (succeeded and self.gather(new_api, depth+1))
                # TODO save info in file
        return finished


    def _choosePlayerMoves(self, api: API) -> List[Any]:
        return api.checkFeasibleMoves(self._playerNumber, self._possibleMoves)

    def _chooseOtherPlayerMoves(self, api: API, other_player_number: int):
        moves = api.checkFeasibleMoves(other_player_number, self._possibleMoves)
        safe_moves = []
        for move in moves:
            if api.isMoveDeadly(other_player_number, move):
                safe_moves.append(move)
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
