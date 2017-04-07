import pygame

from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.randomroutine import RandomRoutine
from pytgf.examples.connect4.builder import create_game

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
    routine = RandomRoutine(gatherer, possible_moves,
                            lambda api: tuple([100 * api.hasWon(player) for player in (1, 2)]),
                            100000, 15, must_keep_temp_files=True, must_write_files=True, max_end_states=100)
    routine.turnByTurn = True
    game_api = loop.api
    routine.routine(1, game_api)


if __name__ == "__main__":
    gather_data()
