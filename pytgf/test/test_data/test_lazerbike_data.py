import unittest

import numpy as np
import pygame

from ...controls.controllers import Passive
from ...data.component import Component
from ...data.gatherer import Gatherer
from ...data.routines import ThroughoutRoutine, RandomRoutine
from ...examples.lazerbike.builder import create_game
from ...examples.lazerbike.gamedata import GO_UP, GO_DOWN, GO_LEFT, GO_RIGHT


class TestLazerbikeData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

        players_positions = {1: (0, 0, GO_RIGHT), 2: (2, 2, GO_LEFT)}

        cls.loop = create_game(({1: Passive, 2: Passive}, {1: 1, 2: 2}), lines=3, columns=3,
                               init_positions=players_positions, speed=200)

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
        cls.routine = ThroughoutRoutine(cls.gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                                        lambda api: {player: 100 * api.hasWon(player) for player in (1, 2)},
                                        must_keep_temp_files=True, must_write_files=True)
        cls.api = cls.loop.api

    def test_gathering_possibility_to_win_in_one_turn(self):
        found = False
        i = 0
        self.a_priori_data, self.a_posteriori_dict = self.routine.routine(1, self.api)
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
        self.a_priori_data, self.a_posteriori_dict = self.routine.routine(1, self.api)
        for i in range(len(self.a_priori_data)):
            if (self.a_priori_data.take((i,)) == np.array([2, 0, 3, 1, 1, 2])).all().all():
                found = True
                break
        if not found:
            self.assertTrue(False)
        else:
            self.assertListEqual(self.a_posteriori_dict[0].take((i,)).get_values().ravel().tolist(), [0., -1., 1.])

    def test_gathering_limited_number(self):
        routine = ThroughoutRoutine(self.gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                                    lambda api: {player: 100*api.hasWon(player) for player in (1, 2)},
                                    must_keep_temp_files=False, must_write_files=False, max_end_states=2)
        a_priori_data, a_posteriori_dict = routine.routine(1, self.api.copy())
        self.assertEqual(len(routine._actionsSequences), 2 * routine._maxEndStates)  # 2 players


class TestLazerbikeRandomData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()

        cls.loop = create_game(({1: Passive, 2: Passive}, {1: 1, 2: 2}))

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
        cls.routine = RandomRoutine(cls.gatherer, (GO_UP, GO_LEFT, GO_RIGHT, GO_DOWN),
                                    lambda api: {player: 100 * api.hasWon(player) for player in (1, 2)},
                                    1, 10, max_end_states=100, must_keep_temp_files=False, must_write_files=False)
        cls.api = cls.loop.api

    def test_actions(self):
        res = None
        beginning_api = self.api.copy()
        while res is None:
            res = self.routine.routine(1, beginning_api.copy())
        for i in range(0, res.shape[0], 2):
            api = beginning_api.copy()
            line = [int(res.loc[i][k]) for k in range(len(res.loc[i])) if res.loc[i][k] == res.loc[i][k]]
            line2 = [int(res.loc[i+1][k]) for k in range(len(res.loc[i+1])) if res.loc[i+1][k] == res.loc[i+1][k]]
            self.assertEqual(len(line), len(line2))
            has_won = {1: bool(line[0]), 2: bool(line2[0])}
            line = line[1:]
            line2 = line2[1:]
            for j in range(len(line)):
                succeeded = api.performMove(1, api.decodeMove(1, line[j]))
                succeeded2 = api.performMove(2, api.decodeMove(2, line2[j]))
                self.assertTrue(succeeded2 and succeeded)
            self.assertTrue(api.isFinished())
            self.assertTrue(api.hasWon(1) == has_won[1])
            self.assertTrue(api.hasWon(2) == has_won[2])
