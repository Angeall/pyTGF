import unittest
import time

import pygame

from gameboard.board import Builder, Board
from examples.lazerbike.AIs.bottest import BotTest
from examples.lazerbike.control.linker import GO_RIGHT, GO_UP, GO_DOWN, LazerBikeBotLinker
from examples.lazerbike.rules.lazerbike import LazerBikeGame
from examples.lazerbike.units.bike import Bike
from game.mainloop import MainLoop


class TestLazerbike(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.width = 720
        self.height = 480
        self.lines = 50
        self.columns = 75
        builder = Builder(self.width, self.height, self.lines, self.columns)
        builder.setBordersColor((0, 125, 125))
        builder.setBackgroundColor((25, 25, 25))
        builder.setTilesVisible(False)
        board = builder.create()  # type: Board
        self.loop = MainLoop(LazerBikeGame(board))

    def tearDown(self):
        if self.loop.executor is not None:
            self.loop.executor.terminate()

    def test_copy(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 25), GO_DOWN, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 25), GO_UP, team=2)
        start = time.time()
        my_copy = self.loop.game.copy()
        print(time.time() - start)
        my_copy.players[1].kill()
        self.assertFalse(my_copy.players[1].isAlive())
        self.assertTrue(self.loop.game.players[1].isAlive())

    def test_draw(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 25), GO_DOWN, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 25), GO_UP, team=2)
        self.assertEqual(len(self.loop.run()), 0)

    def test_draw_4_players(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 25), GO_DOWN, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 25), GO_UP, team=2)
        self.loop.addUnit(Bike(200, 3, max_trace=-1), LazerBikeBotLinker(BotTest(3)), (15, 50), GO_DOWN, team=3)
        self.loop.addUnit(Bike(200, 4, max_trace=-1), LazerBikeBotLinker(BotTest(4)), (30, 50), GO_UP, team=4)
        self.assertEqual(len(self.loop.run()), 0)

    def test_p1_win(self):
        self.loop.addUnit(Bike(100, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 0), GO_RIGHT, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 0), GO_UP, team=2)
        self.assertEqual(self.loop.run()[0].playerNumber, 1)

    def test_p2_win(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 0), GO_DOWN, team=1)
        self.loop.addUnit(Bike(100, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 0), GO_RIGHT, team=2)
        self.assertEqual(self.loop.run()[0].playerNumber, 2)

    def test_p3_win(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 25), GO_DOWN, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 25), GO_UP, team=2)
        self.loop.addUnit(Bike(200, 3, max_trace=-1), LazerBikeBotLinker(BotTest(3)), (30, 35), GO_UP, team=3)
        self.assertEqual(self.loop.run()[0].playerNumber, 3)

    def test_team1_win(self):
        self.loop.addUnit(Bike(200, 1, max_trace=-1), LazerBikeBotLinker(BotTest(1)), (15, 25), GO_DOWN, team=1)
        self.loop.addUnit(Bike(200, 2, max_trace=-1), LazerBikeBotLinker(BotTest(2)), (30, 25), GO_UP, team=2)
        self.loop.addUnit(Bike(200, 3, max_trace=-1), LazerBikeBotLinker(BotTest(3)), (30, 35), GO_UP, team=1)
        winners = self.loop.run()
        self.assertEqual(winners[0].playerNumber, 1)
        self.assertEqual(winners[1].playerNumber, 3)

