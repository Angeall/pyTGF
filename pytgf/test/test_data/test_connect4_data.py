import unittest

import pygame

from pytgf.controls.controllers import Passive
from pytgf.data.component import Component
from pytgf.data.gatherer import Gatherer
from pytgf.data.throughoutroutine import ThroughoutRoutine
from pytgf.examples.connect4.builder import create_game


class TestConnect4Data(unittest.TestCase):

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

    def test_winning_move_not_ignored(self):
        api = self.api.copy()
        api.performMove(1, 0, max_moves=-1)
        api.performMove(2, 3, max_moves=-1)
        api.performMove(1, 2, max_moves=-1)
        api.performMove(2, 3, max_moves=-1)
        api.performMove(1, 0, max_moves=-1)
        api.performMove(2, 3, max_moves=-1)  # 3 pieces aligned for player 2
        moves_list = self.routine._generateMovesList(api)
        for moves in moves_list:
            self.assertTrue(moves[2] == 3 or moves[1] == 3)  # Either P1 blocks the winning move, or the P2 wins
