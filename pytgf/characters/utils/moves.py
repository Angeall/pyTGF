from itertools import product
from typing import Iterable, List, Dict

from ..moves import MoveDescriptor

__author__ = "Anthony Rouneau"

PlayerNumber = int


def getMovesCombinations(moves: Dict[PlayerNumber, Iterable[MoveDescriptor]]) -> List[Dict[int, MoveDescriptor]]:
    """
    Generates al the possible combinations of movements for the given state

    Args:
        moves:
            A dictionary that contains the move to combine for each player
            (key: player number; value: collection of move descriptors)

    Returns:
        A list of dictionaries (e.g. {1: 2, 2: 3} indicates that the player 1 chose the action "2" and the player 2
        chose the action "3")
    """
    player_actions = [list(product([player_number], player_moves)) for player_number, player_moves in moves.items()]
    temp_combinations = list(product(*player_actions))
    return [dict(combination) for combination in temp_combinations]
