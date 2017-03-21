import random
from typing import Union

import pygame

from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.routine import Routine
from pytgf.examples.connect4.builder import create_game
from pytgf.game import API

__author__ = "Anthony Rouneau"


possible_moves = tuple(range(7))


def gather_data():
    pygame.init()
    loop = create_game({1: Passive, 2: Passive}, 720, 720, False)

    a_priori_methods = [lambda api: api.getLastMove(1), lambda api: api.getLastMove(2)]
    a_priori_title = ["p1_last_move", "p2_last_move"]
    for i in range(-1,  loop.game.board.lines + 1):
        for j in range(-1, loop.game.board.columns + 1):
            cur_id = (i, j)
            a_priori_methods.append(lambda api, tile_id=cur_id: api.getTileByteCode(tile_id))
            a_priori_title.append("(" + str(i) + ", " + str(j) + ")")
    a_posteriori_methods = [lambda api: 1000 if api.hasWon(1) else 0, lambda api: 1000 if api.hasWon(2) else 0]
    a_posteriori_titles = ["p1_final_points", "p2_final_points"]
    a_priori_components = []
    a_posteriori_components = []
    for i in range(len(a_priori_methods)):
        a_priori_components.append(Component(a_priori_methods[i], a_priori_title[i]))
    for i in range(len(a_posteriori_methods)):
        a_posteriori_components.append(Component(a_posteriori_methods[i], a_posteriori_titles[i]))
    gatherer = Gatherer(a_priori_components, a_posteriori_components)
    routine = Routine(gatherer, possible_moves,
                      lambda api: tuple([100 * api.hasWon(player) for player in (1, 2)]),
                      must_keep_temp_files=True, must_write_files=True)
    game_api = loop.api
    a_priori_data, a_posteriori_dict = routine.routine(1, game_api)


def simulate_randomMoves(initial_state: API, nb_moves: int) -> Union[API, None]:
    """
    Performs random moves for a 2-players connect 4 game

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
                state = simulate_randomMoves(state, nb_moves - 1)
                if state is None:
                    continue
                else:
                    return state
        return None

if __name__ == "__main__":
    gather_data()
