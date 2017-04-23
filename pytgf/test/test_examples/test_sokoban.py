import unittest

import pygame

from ...controls.controllers import Passive
from ...examples.sokoban.parsing.builder import SokobanBoardBuilder
from ...examples.sokoban.parsing.parser import wall, hole, box, player_tile, winning, classical_tile
from ...examples.sokoban.units.box import Box
from ...game.realtime import RealTimeMainLoop


class TestSokoban(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.parserResult = [[player_tile, wall, wall], [box, wall, wall],
                             [classical_tile, classical_tile, wall], [hole, classical_tile, winning]]
        self.controller = Passive
        builder = SokobanBoardBuilder(self.width, self.height, self.parserResult, [self.controller], 1000)
        builder.setBordersColor((0, 0, 0))
        builder.setTilesVisible(True)
        self.loop = builder.createGame()  # type: RealTimeMainLoop
        self.wrapper = list(self.loop.wrappers.keys())[0]
        if isinstance(self.loop.wrappers[self.wrapper], Box):
            linkers_list = list(self.loop.wrappers.keys())
            self.wrapper = linkers_list[1]

    def tearDown(self):
        if self.loop.executor is not None:
            self.loop.executor.terminate()

    def test_push_box_in_hole(self):
        self.loop._prepareLoop()
        self.wrapper._sendActionToGame((2, 0))
        self.wrapper._sendActionToGame((3, 2))
        pushed_box = None
        for unit in self.loop.game.players.values():
            if isinstance(unit, Box):
                pushed_box = unit
        self.assertTrue(pushed_box is not None)
        self.assertTrue(pushed_box is self.loop.game.getTileOccupants((1, 0))[0])
        self.assertTrue(self.loop.game.board.getTileById((3, 0)).deadly)
        self.loop.run(60)
        self.assertFalse(self.loop.game.board.getTileById((3, 0)).deadly)

    def test_win(self):
        self.loop._prepareLoop()
        self.wrapper._sendActionToGame((2, 0))
        self.wrapper._sendActionToGame((3, 2))
        self.assertEqual(len(self.loop.run(60)), 1)
