import unittest

from typing import List, Dict

from pytgf.controls.controllers import Passive
from pytgf.controls.wrappers import ControllerWrapper
from pytgf.examples.connect4.builder import create_game


class TestConnect4(unittest.TestCase):
    def setUp(self):
        self.mainLoop = create_game({1: Passive, 2: Passive}, 360, 360)
        wrappers = list(self.mainLoop.linkers.keys())  # type: List[ControllerWrapper]
        self.playersWrappers = None  # type: Dict[int, ControllerWrapper]
        self.playersWrappers = {wrapper.controller.playerNumber: wrapper
                                for wrapper in wrappers}

    def test_easy_win(self):
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)  # Plays after the end of the game => should not influence
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(1))

    def test_easy_win2(self):
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 2, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(2))

    def test_diagonal_win(self):
        self.mainLoop.api.performMove(1, 0, max_moves=-1)
        self.mainLoop.api.performMove(2, 1, max_moves=-1)
        self.mainLoop.api.performMove(1, 1, max_moves=-1)
        self.mainLoop.api.performMove(2, 2, max_moves=-1)
        self.mainLoop.api.performMove(1, 2, max_moves=-1)
        self.mainLoop.api.performMove(2, 3, max_moves=-1)
        self.mainLoop.api.performMove(1, 2, max_moves=-1)
        self.mainLoop.api.performMove(2, 3, max_moves=-1)
        self.mainLoop.api.performMove(1, 3, max_moves=-1)
        self.mainLoop.api.performMove(2, 5, max_moves=-1)
        self.mainLoop.api.performMove(1, 3, max_moves=-1)
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(1))
