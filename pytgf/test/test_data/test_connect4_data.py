import unittest

import pygame

from ...controls.controllers import Passive
from ...data.component import Component
from ...data.gatherer import Gatherer
from ...data.routines import ThroughoutRoutine, RandomRoutine
from ...examples.connect4.builder import create_game


class TestConnect4ThoroughData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.init()
        cls.loop = create_game({1: Passive, 2: Passive}, 720, 720, False)

        a_priori_methods = [lambda api: api.getLastMove(1), lambda api: api.getLastMove(2)]
        a_priori_title = ["p1_last_move", "p2_last_move"]
        for i in range(-1, cls.loop.game.board.lines + 1):
            for j in range(-1, cls.loop.game.board.columns + 1):
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
        cls.gatherer = Gatherer(a_priori_components, a_posteriori_components)
        cls.routine = ThroughoutRoutine(cls.gatherer, tuple(range(7)),
                                        lambda api: tuple([100*api.hasWon(player) for player in (1, 2)]),
                                        must_keep_temp_files=False, must_write_files=False)
        cls.routine.turnByTurn = True
        cls.api = cls.loop.api

    def test_opponent_winning_move_not_ignored(self):
        api = self.api.copy()
        api.performMove(1, 0)
        api.performMove(2, 3)
        api.performMove(1, 2)
        api.performMove(2, 3)
        api.performMove(1, 0)
        api.performMove(2, 3)  # 3 pieces aligned for player 2
        moves_list = self.routine._generateMovesList(api)
        for moves in moves_list:
            self.assertTrue(moves[2] == 3 or moves[1] == 3)  # Either P1 blocks the winning move, or the P2 wins

    def test_self_winning_move_not_ignored(self):
        api = self.api.copy()
        api.performMove(1, 0)
        api.performMove(2, 3)
        api.performMove(1, 0)
        api.performMove(2, 3)
        api.performMove(1, 0)
        api.performMove(2, 3)  # 3 pieces aligned for player 2
        moves_list = self.routine._generateMovesList(api)
        for moves in moves_list:
            self.assertTrue(moves[1] == 0)  # Only move that makes sense


class TestConnect4RandomData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pygame.init()
        cls.loop = create_game({1: Passive, 2: Passive}, 720, 720, False)

        a_priori_methods = [lambda api: api.getLastMove(1), lambda api: api.getLastMove(2)]
        a_priori_title = ["p1_last_move", "p2_last_move"]
        for i in range(-1, cls.loop.game.board.lines + 1):
            for j in range(-1, cls.loop.game.board.columns + 1):
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
        cls.routine = RandomRoutine(gatherer, tuple(range(7)),
                                    lambda api: tuple([100 * api.hasWon(player) for player in (1, 2)]),
                                    1, 15, must_keep_temp_files=False, must_write_files=False, max_end_states=20)
        cls.routine.turnByTurn = True
        cls.api = cls.loop.api
        cls.api.game.turnByTurn = True

    def test_actions(self):
        res = None
        beginning_api = create_game({1: Passive, 2: Passive}, 720, 720, False).api
        beginning_api.game.turnByTurn = True
        while res is None or res.shape == ():
            res = self.routine.routine(1, beginning_api.copy())
        for i in range(0, res.shape[0], 2):
            api = beginning_api.copy()
            line = [int(res.loc[i][k]) for k in range(len(res.loc[i])) if res.loc[i][k] == res.loc[i][k]]
            line2 = [int(res.loc[i+1][k]) for k in range(len(res.loc[i+1])) if res.loc[i+1][k] == res.loc[i+1][k]]
            has_won = {1: bool(line[0]), 2: bool(line2[0])}
            line = line[1:]
            line2 = line2[1:]
            for j in range(len(line)):
                succeeded2 = True
                succeeded = api.performMove(1, line[j])
                if not api.isFinished():
                    succeeded2 = api.performMove(2, line2[j])
                self.assertTrue(succeeded2 and succeeded)
            self.assertTrue(api.isFinished())
            self.assertTrue(api.hasWon(1) == has_won[1])
            self.assertTrue(api.hasWon(2) == has_won[2])
