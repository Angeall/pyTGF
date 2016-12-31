import unittest

import pygame

from board.boards.square_board import SquareBoardBuilder
from examples.lazerbike.AIs.bottest import BotTest
from examples.lazerbike.controls.allowed_moves import GO_UP, GO_DOWN, GO_RIGHT
from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.units.bike import Bike


class TestLazerbike(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.lines = 50
        self.columns = 75
        builder = SquareBoardBuilder(self.width, self.height, self.lines, self.columns)
        builder.setBordersColor((0, 125, 125))
        builder.setBackgroundColor((25, 25, 25))
        builder.setTilesVisible(False)
        board = builder.create()
        self.game = LazerBikeGame(board)

    def test_draw(self):
        self.game.addUnit(Bike(200, 1, max_trace=-1), BotTest(1), (15, 25), GO_DOWN, team=1)
        self.game.addUnit(Bike(200, 2, max_trace=-1), BotTest(2), (30, 25), GO_UP, team=2)
        self.assertEqual(len(self.game.run()), 0)

    def test_draw_4_players(self):
        self.game.addUnit(Bike(200, 1, max_trace=-1), BotTest(1), (15, 25), GO_DOWN, team=1)
        self.game.addUnit(Bike(200, 2, max_trace=-1), BotTest(2), (30, 25), GO_UP, team=2)
        self.game.addUnit(Bike(200, 3, max_trace=-1), BotTest(3), (15, 50), GO_DOWN, team=3)
        self.game.addUnit(Bike(200, 4, max_trace=-1), BotTest(4), (30, 50), GO_UP, team=4)
        self.assertEqual(len(self.game.run()), 0)

    def test_p1_win(self):
        self.game.addUnit(Bike(100, 1, max_trace=-1), BotTest(1), (15, 0), GO_RIGHT, team=1)
        self.game.addUnit(Bike(200, 2, max_trace=-1), BotTest(2), (30, 0), GO_UP, team=2)
        self.assertEqual(self.game.run(), (1,))

    def test_p2_win(self):
        self.game.addUnit(Bike(200, 1, max_trace=-1), BotTest(1), (15, 0), GO_DOWN, team=1)
        self.game.addUnit(Bike(100, 2, max_trace=-1), BotTest(2), (30, 0), GO_RIGHT, team=2)
        self.assertEqual(self.game.run(), (2,))

    def test_p3_win(self):
        self.game.addUnit(Bike(200, 1, max_trace=-1), BotTest(1), (15, 25), GO_DOWN, team=1)
        self.game.addUnit(Bike(200, 2, max_trace=-1), BotTest(2), (30, 25), GO_UP, team=2)
        self.game.addUnit(Bike(200, 3, max_trace=-1), BotTest(3), (30, 35), GO_UP, team=3)
        self.assertEqual(self.game.run(), (3,))

    def test_team1_win(self):
        self.game.addUnit(Bike(200, 1, max_trace=-1), BotTest(1), (15, 25), GO_DOWN, team=1)
        self.game.addUnit(Bike(200, 2, max_trace=-1), BotTest(2), (30, 25), GO_UP, team=2)
        self.game.addUnit(Bike(200, 3, max_trace=-1), BotTest(3), (30, 35), GO_UP, team=1)
        self.assertEqual(self.game.run(), (1, 3))

