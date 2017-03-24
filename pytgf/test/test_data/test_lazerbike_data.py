import unittest

import numpy as np
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

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.width = 720
        cls.height = 480
        cls.lines = 3
        cls.columns = 3
        builder = Builder(cls.width, cls.height, cls.lines, cls.columns)
        builder.setBordersColor((0, 125, 125))
        builder.setBackgroundColor((25, 25, 25))
        builder.setTilesVisible(False)
        board = builder.create()  # type: Board
        cls.loop = MainLoop(LazerBikeAPI(LazerBikeCore(board)))
        b1 = Bike(200, 1, max_trace=-1)
        cls.loop.addUnit(b1, LazerBikeBotControllerWrapper(Passive(1)), (0, 0), GO_RIGHT,
                         team=1)
        b2 = Bike(200, 2, max_trace=-1)
        cls.loop.addUnit(b2, LazerBikeBotControllerWrapper(Passive(2)), (2, 2), GO_LEFT,
                         team=2)

        a_priori_methods = [lambda api: api.getPlayerLocation(1)[0], lambda api: api.getPlayerLocation(1)[1],
                            lambda api: api.getCurrentDirection(1),
                            lambda api: api.getPlayerLocation(2)[0], lambda api: api.getPlayerLocation(2)[1],
                            lambda api: api.getCurrentDirection(2)]
        a_priori_title = ["location_x", "location_y", "direction", "opponent_x", "opponent_y", "opponent_direction"]
        a_posteriori_methods = [lambda api: 1000 if api.hasWon(1) else 0]
        a_posteriori_titles = ["final_points"]
        a_priori_components = []
        a_posteriori_components = []
        for i in range(len(a_priori_methods)):
            a_priori_components.append(Component(a_priori_methods[i], a_priori_title[i]))
        for i in range(len(a_posteriori_methods)):
            a_posteriori_components.append(Component(a_posteriori_methods[i], a_posteriori_titles[i]))
        cls.gatherer = Gatherer(a_priori_components, a_posteriori_components)
        cls.routine = Routine(cls.gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                              lambda api: tuple([100*api.hasWon(player) for player in (1, 2)]),
                              must_keep_temp_files=True, must_write_files=True)
        cls.api = cls.loop.api
        cls.a_priori_data, cls.a_posteriori_dict = cls.routine.routine(1, cls.api)

    def test_gathering_possibility_to_win_in_one_turn(self):
        found = False
        i = 0
        for i in range(len(self.a_priori_data)):
            if (self.a_priori_data.take((i,)) == np.array([1, 1, 0, 0, 2, 1])).all().all():
                found = True
                break
        if not found:
            self.assertTrue(False)
        else:
            self.assertListEqual(self.a_posteriori_dict[3].take((i,)).get_values().ravel().tolist(), [0., 1., 1.])

    def test_gathering_no_way_out(self):
        found = False
        i = 0
        for i in range(len(self.a_priori_data)):
            if (self.a_priori_data.take((i,)) == np.array([2, 0, 3, 1, 1, 2])).all().all():
                found = True
                break
        if not found:
            self.assertTrue(False)
        else:
            self.assertListEqual(self.a_posteriori_dict[0].take((i,)).get_values().ravel().tolist(), [0., -1., 1.])

