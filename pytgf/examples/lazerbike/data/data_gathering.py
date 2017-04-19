import pygame

from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.routines.randomroutine import RandomRoutine
from pytgf.examples.lazerbike.builder import create_game
from pytgf.examples.lazerbike.gamedata import GO_LEFT, GO_UP, GO_RIGHT, GO_DOWN

__author__ = "Anthony Rouneau"


possible_moves = (GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT)


def gather_data():
    pygame.init()

    loop = create_game(({1: Passive, 2: Passive}, {1: 1, 2: 2}), graphics=False)

    a_priori_methods = [lambda api: api.getPlayerLocation(1)[0], lambda api: api.getPlayerLocation(1)[1],
                        lambda api: api.getCurrentDirection(1),
                        lambda api: api.getPlayerLocation(2)[0], lambda api: api.getPlayerLocation(2)[1],
                        lambda api: api.getCurrentDirection(2)]
    a_priori_title = ["location_x", "location_y", "direction", "opponent_x", "opponent_y", "opponent_direction"]
    for i in range(-1,  16):
        for j in range(-1, 16):
            cur_id = (i, j)
            a_priori_methods.append(lambda api, tile_id=cur_id: api.getTileByteCode(tile_id))
            a_priori_title.append("(" + str(i) + ", " + str(j) + ")")
    a_posteriori_methods = [lambda api: 1000 if api.hasWon(1) else 0]
    a_posteriori_titles = ["final_points"]
    a_priori_components = []
    a_posteriori_components = []
    for i in range(len(a_priori_methods)):
        a_priori_components.append(Component(a_priori_methods[i], a_priori_title[i]))
    for i in range(len(a_posteriori_methods)):
        a_posteriori_components.append(Component(a_posteriori_methods[i], a_posteriori_titles[i]))
    gatherer = Gatherer(a_priori_components, a_posteriori_components)
    routine = RandomRoutine(gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                            lambda api: tuple([100 * api.hasWon(player) for player in (1, 2)]),
                            5000000, 40, max_end_states=100, max_step_per_moves=1,
                            must_keep_temp_files=True, must_write_files=True)
    game_api = loop.api
    routine.routine(1, game_api)


if __name__ == "__main__":
    gather_data()
