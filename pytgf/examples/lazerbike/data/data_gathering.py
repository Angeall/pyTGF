import random
from typing import Union

from pytgf.examples.lazerbike.gamedata import GO_LEFT, GO_UP, GO_RIGHT, GO_DOWN
from pytgf.game import API

__author__ = "Anthony Rouneau"


possible_moves = (GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT)


def simulateRandomMoves(initial_state: API, nb_moves: int) -> Union[API, None]:
    """
    Performs random moves for a 2-players lazerbike game

    Args:
        initial_state:
        nb_moves:

    Returns:

    """
    if nb_moves <= 0:
        return initial_state
    else:
        p1_moves = initial_state.checkFeasibleMoves(1, possible_moves)
        p2_moves = initial_state.checkFeasibleMoves(2, possible_moves)
        if len(p1_moves) == 0 or len(p2_moves) == 0 or \
                not initial_state.isPlayerAlive(1) or not initial_state.isPlayerAlive(2):
            return None
        random.shuffle(p1_moves)
        random.shuffle(p2_moves)
        for p1_move in p1_moves:
            for p2_move in p2_moves:
                succeeded, state = initial_state.simulateMoves({1: p1_move, 2: p2_move})
                if not succeeded or state is None:
                    continue
                state = simulateRandomMoves(state, nb_moves-1)
                if state is None:
                    continue
                else:
                    return state
        return None
