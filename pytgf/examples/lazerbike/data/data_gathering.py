import pygame

from pytgf.board import Builder
from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.randomroutine import RandomRoutine
from pytgf.examples.lazerbike.control import LazerBikeBotControllerWrapper
from pytgf.examples.lazerbike.gamedata import GO_LEFT, GO_UP, GO_RIGHT, GO_DOWN
from pytgf.examples.lazerbike.rules import LazerBikeAPI
from pytgf.examples.lazerbike.rules import LazerBikeCore
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.game.mainloop import MainLoop

__author__ = "Anthony Rouneau"


possible_moves = (GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT)


def gather_data():
    pygame.init()
    width = 720
    height = 480
    lines = 15
    columns = 15
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()
    board.graphics = None
    loop = MainLoop(LazerBikeAPI(LazerBikeCore(board)))
    b1 = Bike(200, 1, max_trace=-1, graphics=False)
    loop.addUnit(b1, LazerBikeBotControllerWrapper(Passive(1)), (2, 2), GO_RIGHT,
                 team=1)
    b2 = Bike(200, 2, max_trace=-1, graphics=False)
    loop.addUnit(b2, LazerBikeBotControllerWrapper(Passive(2)), (12, 12), GO_LEFT,
                 team=2)

    a_priori_methods = [lambda api: api.getPlayerLocation(1)[0], lambda api: api.getPlayerLocation(1)[1],
                        lambda api: api.getCurrentDirection(1),
                        lambda api: api.getPlayerLocation(2)[0], lambda api: api.getPlayerLocation(2)[1],
                        lambda api: api.getCurrentDirection(2)]
    a_priori_title = ["location_x", "location_y", "direction", "opponent_x", "opponent_y", "opponent_direction"]
    for i in range(-1,  board.lines + 1):
        for j in range(-1, board.columns + 1):
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
                            1, 10, max_end_states=100, max_step_per_moves=1,
                            must_keep_temp_files=True, must_write_files=True)
    game_api = loop.api
    routine.routine(1, game_api)


if __name__ == "__main__":
    gather_data()
