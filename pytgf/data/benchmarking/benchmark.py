import time
from typing import List

from pytgf.controls.events import WakeEvent
from pytgf.game.turnbased import TurnBasedAPI
from ...controls.controllers import Bot
from ...controls.events import BotEvent
from ...game import API

__author__ = "Anthony Rouneau"


DRAW = 0
WIN = 1
LOSE = -1


class Benchmark:
    def __init__(self, starting_api: API, controllers: List[Bot]):
        """
        Creates a benchmark object which can be used to confront multiple controllers
        
        Args:
            starting_api: The API from which all the game simulation will be started  
            controllers: The controllers (in order if there is one) that will play this game
        """
        self._startingApi = starting_api
        self._controllers = controllers
        for controller in self._controllers:
            controller.gameState = self._startingApi.copy().game
            controller.getReady()
        self._results = self._initDict()
        self._eventsToSend = self._initDict()

    def _initDict(self):
        return {controller.playerNumber: [] for controller in self._controllers}

    def benchmark(self, nb_games: int):
        for i in range(nb_games):
            start_time = time.time()
            start = True
            self._eventsToSend = self._initDict()
            starting_copy = self._startingApi.copy()
            for controller in self._controllers:
                controller.gameState = starting_copy.copy().game
            while not starting_copy.isFinished():
                for controller in self._controllers:
                    if start:
                        start = False
                        events = [WakeEvent()]
                    else:
                        events = self._eventsToSend[controller.playerNumber]
                        self._eventsToSend[controller.playerNumber] = []
                    controller.reactToEvents(events)
                    if isinstance(starting_copy, TurnBasedAPI):
                        move = controller.moves.get()
                        self._addMessageToAll(BotEvent(controller.playerNumber, move))
                        starting_copy.performMove(controller.playerNumber, move)
                if not isinstance(starting_copy, TurnBasedAPI):
                    moves = {controller: controller.moves.get() for controller in self._controllers}
                    for controller, move in moves.items():
                        self._addMessageToAll(BotEvent(controller.playerNumber, move))
                    for controller, move in moves.items():
                        starting_copy.performMove(controller.playerNumber, move)
            for player_number in starting_copy.getPlayerNumbers():
                res = DRAW
                if not starting_copy.isPlayerAlive(player_number):
                    res = LOSE
                if starting_copy.hasWon(player_number):
                    res = WIN
                self._results[player_number].append(res)
            print('TIME:', time.time() - start_time)

        wins = self._results
        self._results = self._initDict()
        self._eventsToSend = self._initDict()
        return wins

    def _addMessageToAll(self, event: BotEvent):
        for player_number in self._eventsToSend:
            self._eventsToSend[player_number].append(event)



