import unittest

import pygame

from gameboard.tile import Tile
from controls.controllers.passive import PassiveController
from examples.sokoban.parser.builder import SokobanBoardBuilder
from examples.sokoban.tiles.hole import Hole
from examples.sokoban.tiles.wall import Wall
from examples.sokoban.tiles.winning import Winning
from examples.sokoban.units.box import Box
from examples.sokoban.units.sokobandrawstick import SokobanDrawstick
from game.mainloop import MainLoop


class TestSokoban(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.parserResult = [[SokobanDrawstick, Wall, Wall], [Box, Wall, Wall],
                             [Tile, Tile, Wall], [Hole, Tile, Winning]]
        self.controller = PassiveController
        builder = SokobanBoardBuilder(self.width, self.height, self.parserResult, [self.controller], 1000)
        builder.setBordersColor((0, 0, 0))
        builder.setTilesVisible(True)
        self.loop = builder.createGame()  # type: MainLoop
        self.linker = list(self.loop.linkers.keys())[0]
        if isinstance(self.loop.linkers[self.linker], Box):
            linkers_list = list(self.loop.linkers.keys())
            self.linker = linkers_list[1]

    def tearDown(self):
        if self.loop.executor is not None:
            self.loop.executor.terminate()

    def test_push_box_in_hole(self):
        self.loop.game._winningTiles.append((3, 0))
        self.loop.game.board.getTileById((3, 0)).addOccupant(self.loop.game._endingUnit)
        self.loop._prepareLoop()
        self.loop._getProcessPipeConnection(self.linker).send((1, 0))
        self.loop._getProcessPipeConnection(self.linker).send((2, 0))
        self.loop._getProcessPipeConnection(self.linker).send((3, 1))
        box = None
        for unit in self.loop.linkers.values():
            if isinstance(unit, Box):
                box = unit
        self.assertTrue(box is not None)
        self.assertTrue(box in self.loop.game.board.getTileById((1, 0)))
        self.assertTrue(self.loop.game.board.getTileById((3, 0)).deadly)
        self.loop.run(60)
        self.assertFalse(self.loop.game.board.getTileById((3, 0)).deadly)

    def test_win(self):
        self.loop._prepareLoop()
        self.loop._getProcessPipeConnection(self.linker).send((1, 0))
        self.loop._getProcessPipeConnection(self.linker).send((2, 0))
        self.loop._getProcessPipeConnection(self.linker).send((3, 2))
        self.assertEqual(len(self.loop.run(60)), 1)
