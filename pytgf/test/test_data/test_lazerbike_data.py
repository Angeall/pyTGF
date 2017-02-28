import unittest

import pygame

from pytgf.board import Board
from pytgf.board import Builder
from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.routine import Routine
from pytgf.examples.lazerbike.control import LazerBikeBotControllerWrapper
from pytgf.examples.lazerbike.gamedata import GO_UP, GO_DOWN, GO_LEFT, GO_RIGHT
from pytgf.examples.lazerbike.rules import LazerBikeAPI
from pytgf.examples.lazerbike.rules import LazerBikeCore
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.game.mainloop import MainLoop


class TestLazerbikeData(unittest.TestCase):

    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.lines = 5
        self.columns = 5
        builder = Builder(self.width, self.height, self.lines, self.columns)
        builder.setBordersColor((0, 125, 125))
        builder.setBackgroundColor((25, 25, 25))
        builder.setTilesVisible(False)
        board = builder.create()  # type: Board
        self.loop = MainLoop(LazerBikeAPI(LazerBikeCore(board)))
        b1 = Bike(200, 1, max_trace=-1)
        b1.turn(3)
        self.loop.addUnit(b1, LazerBikeBotControllerWrapper(Passive(1)), (1, 1), GO_DOWN,
                          team=1)
        b2 = Bike(200, 2, max_trace=-1)
        b2.turn(1)
        self.loop.addUnit(b2, LazerBikeBotControllerWrapper(Passive(2)), (3, 3), GO_UP,
                          team=2)

        a_priori_methods = [lambda api: api.getPlayerLocation(1)[0], lambda api: api.getPlayerLocation(1)[1],
                            lambda api: api.getPlayerLocation(2)[0], lambda api: api.getPlayerLocation(2)[1]]
        a_priori_title = ["location_x", "location_y", "opponent_x", "opponent_y"]
        a_posteriori_methods = [lambda api: 1000 if api.hasWon(1) else 0]
        a_posteriori_titles = ["final_points"]
        a_priori_components = []
        a_posteriori_components = []
        for i in range(len(a_priori_methods)):
            a_priori_components.append(Component(a_priori_methods[i], a_priori_title[i]))
        for i in range(len(a_posteriori_methods)):
            a_posteriori_components.append(Component(a_posteriori_methods[i], a_posteriori_titles[i]))
        self.gatherer = Gatherer(a_priori_components, a_posteriori_components)
        self.routine = Routine(self.gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                               lambda api: tuple([100*api.hasWon(player) for player in (1, 2)]))
        self.api = self.loop.api

    def test_gathering(self):
        self.routine.routine(1, self.api)
        self.loop.run()
