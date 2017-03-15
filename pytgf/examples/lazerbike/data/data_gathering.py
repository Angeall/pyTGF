import random
from typing import Union

import pygame

from pytgf.board import Builder
from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.routine import Routine
from pytgf.examples.lazerbike.control import LazerBikeBotControllerWrapper
from pytgf.examples.lazerbike.gamedata import GO_LEFT, GO_UP, GO_RIGHT, GO_DOWN
from pytgf.examples.lazerbike.rules import LazerBikeAPI
from pytgf.examples.lazerbike.rules import LazerBikeCore
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.game import API
from pytgf.game.mainloop import MainLoop

__author__ = "Anthony Rouneau"


possible_moves = (GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT)


def gather_data():
    pygame.init()
    width = 720
    height = 480
    lines = 20
    columns = 20
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()
    board.graphics = None
    loop = MainLoop(LazerBikeAPI(LazerBikeCore(board)))
    b1 = Bike(200, 1, max_trace=-1, graphics=False)
    loop.addUnit(b1, LazerBikeBotControllerWrapper(Passive(1)), (0, 0), GO_RIGHT,
                 team=1)
    b2 = Bike(200, 2, max_trace=-1, graphics=False)
    loop.addUnit(b2, LazerBikeBotControllerWrapper(Passive(2)), (2, 2), GO_LEFT,
                 team=2)

    a_priori_methods = [lambda api: api.getPlayerLocation(1)[0], lambda api: api.getPlayerLocation(1)[1],
                        lambda api: api.getCurrentDirection(1),
                        lambda api: api.getPlayerLocation(2)[0], lambda api: api.getPlayerLocation(2)[1],
                        lambda api: api.getCurrentDirection(2)]
    a_priori_title = ["location_x", "location_y", "direction", "opponent_x", "opponent_y", "opponent_direction"]
    for i in range(board.lines):
        for j in range(board.columns):
            a_priori_methods.append(lambda api: api.getTileByteCode(i, j))
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
    routine = Routine(gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                      lambda api: tuple([100 * api.hasWon(player) for player in (1, 2)]),
                      must_keep_temp_files=True, must_write_files=True)
    game_api = loop.api
    a_priori_data, a_posteriori_dict = routine.routine(1, game_api)


def simulate_randomMoves(initial_state: API, nb_moves: int) -> Union[API, None]:
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
                state = simulate_randomMoves(state, nb_moves - 1)
                if state is None:
                    continue
                else:
                    return state
        return None

if __name__ == "__main__":
    gather_data()
