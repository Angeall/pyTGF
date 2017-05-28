import unittest
from typing import List, Dict

import pandas as pd

from ...controls.controllers import Passive
from ...controls.wrappers import ControllerWrapper
from ...examples.connect4.builder import create_game


class TestConnect4(unittest.TestCase):
    def setUp(self):
        self.mainLoop = create_game({1: Passive, 2: Passive}, 360, 360)
        wrappers = list(self.mainLoop.wrappers.keys())  # type: List[ControllerWrapper]
        self.playersWrappers = None  # type: Dict[int, ControllerWrapper]
        self.playersWrappers = {wrapper.controller.playerNumber: wrapper
                                for wrapper in wrappers}

    def test_easy_win(self):
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)  # Plays after the end of the game => should not influence
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(1))

    def test_easy_win2(self):
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 2)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(2))

    def test_diagonal_win(self):
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 1)
        self.mainLoop.api.performMove(2, 2)
        self.mainLoop.api.performMove(1, 2)
        self.mainLoop.api.performMove(2, 3)
        self.mainLoop.api.performMove(1, 2)
        self.mainLoop.api.performMove(2, 3)
        self.mainLoop.api.performMove(1, 3)
        self.mainLoop.api.performMove(2, 5)
        self.mainLoop.api.performMove(1, 3)
        self.assertTrue(self.mainLoop.api.isFinished())
        self.assertTrue(self.mainLoop.api.hasWon(1))

    def test_unfeasible(self):
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 0)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 0)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 0)
        succeeded = self.mainLoop.api.performMove(1, 0)
        self.assertFalse(succeeded)

    def test_action_history(self):
        self.mainLoop.api.performMove(1, 1)
        self.mainLoop.api.performMove(2, 2)
        self.mainLoop.api.performMove(1, 3)
        self.mainLoop.api.performMove(2, 4)
        self.mainLoop.api.performMove(1, 5)
        self.mainLoop.api.performMove(2, 6)
        self.mainLoop.api.performMove(1, 0)
        self.mainLoop.api.performMove(2, 1)
        self.mainLoop.api.performMove(1, 2)
        self.mainLoop.api.performMove(2, 3)

        self.assertEqual(self.mainLoop.api.getActionsHistory(1), [1, 3, 5, 0, 2])
        self.assertEqual(self.mainLoop.api.getActionsHistory(2), [2, 4, 6, 1, 3])
        is_equal = self.mainLoop.api.getAllActionsHistories() == pd.DataFrame([[1, 3, 5, 0, 2], [2, 4, 6, 1, 3]])
        self.assertTrue(is_equal.all().all())
