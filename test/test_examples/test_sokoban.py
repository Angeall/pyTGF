import unittest

import pygame

from board.tile import Tile
from characters.controllers.passive import PassiveController
from examples.sokoban.gameloop.loop import SokobanGame
from examples.sokoban.parser.builder import SokobanBoardBuilder
from examples.sokoban.tiles.hole import Hole
from examples.sokoban.tiles.wall import Wall
from examples.sokoban.tiles.winning import Winning
from examples.sokoban.units.box import Box
from examples.sokoban.units.sokobandrawstick import SokobanDrawstick


class TestSokoban(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.parserResult = [[SokobanDrawstick, Tile, Wall], [Box, Tile, Wall], [Hole, Winning, Tile]]
        self.controller = PassiveController
        builder = SokobanBoardBuilder(self.width, self.height, self.parserResult, [self.controller], 1000)
        builder.setBordersColor((0, 0, 0))
        builder.setTilesVisible(True)
        self.game = builder.createGame()
        self.controller = list(self.game.controllers.keys())[0]
        if isinstance(self.game.controllers[self.controller], Box):
            self.controller = list(self.game.controllers.keys())[1]

    def test_push_box_in_hole(self):
        self.game.game._winningTiles.append((1, 0))
        self.controller.moves.put((1, 0))
        self.assertTrue(self.game.game.board.getTileById((2, 0)).deadly)
        self.game.run(60)
        box = None
        for unit in self.game.controllers.values():
            if isinstance(unit, Box):
                box = unit
        self.assertTrue(box is not None)
        self.assertEqual(self.game.game._units[box], (2, 0))
        self.assertFalse(self.game.game.board.getTileById((2, 0)).deadly)

    def test_win(self):
        self.game.game._winningTiles.append((1, 0))
        self.controller.moves.put((1, 0))
        self.controller.moves.put((2, 0))
        self.controller.moves.put((2, 1))
        self.assertEqual(len(self.game.run(60)), 1)
