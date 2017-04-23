from typing import List

from ...controls.controllers import Bot
from ...controls.events import BotEvent
from ...game import API

__author__ = "Anthony Rouneau"


class Benchmark:
    def __init__(self, starting_api: API, controllers: List[Bot], turn_by_turn: bool=False):
        """
        Creates a benchmark object which can be used to confront multiple controllers
        
        Args:
            starting_api: The API from which all the game simulation will be started  
            controllers: The controllers (in order if there is one) that will play this game
            turn_by_turn: If True, the game will be played turn by turn
        """
        self._startingApi = starting_api
        self._controllers = controllers
        self._turnByTurn = turn_by_turn
        self._wins = {controller.playerNumber: 0 for controller in self._controllers}

    def benchmark(self, nb_games: int):
        for i in range(nb_games):
            starting_copy = self._startingApi.copy()

            while not starting_copy.isFinished():
                for controller in self._controllers:
                    controller.gameState = starting_copy.game
                    controller.reactToEvents([BotEvent(other_controller.playerNumber,
                                                       starting_copy.game.getUnitForNumber(
                                                           other_controller.playerNumber).lastAction)
                                              for other_controller in self._controllers])
                    if self._turnByTurn:
                        move = controller.moves.get()
                        starting_copy.performMove(controller.playerNumber, move, turn_by_turn=True)
                        if starting_copy.isFinished():
                            break
                if not self._turnByTurn:
                    moves = {controller: controller.moves.get() for controller in self._controllers}
                    for controller, move in moves.items():
                        starting_copy.performMove(controller.playerNumber, move)
            for winner in starting_copy.game.winningPlayers:
                self._wins[winner.playerNumber] += 1

        wins = self._wins
        self._wins = {controller.playerNumber: 0 for controller in self._controllers}
        return wins



