from typing import List

from pytgf.board import Builder
from pytgf.controls.controllers import Bot
from pytgf.controls.events import BotEvent
from pytgf.examples.lazerbike.gamedata import GO_RIGHT, GO_LEFT
from pytgf.examples.lazerbike.rules import LazerBikeAPI, LazerBikeCore
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.game import API
from res.AIs.lazerbike_randombot import RandomBot

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
                    moves = [controller.moves.get() for controller in self._controllers]
                    for move in moves:
                        starting_copy.performMove(controller.playerNumber, move)
            for winner in starting_copy.game.winningPlayers:
                self._wins[winner.playerNumber] += 1

        wins = self._wins
        self._wins = {controller.playerNumber: 0 for controller in self._controllers}
        return wins


if __name__ == "__main__":
    width = 720
    height = 480
    lines = 20
    columns = 20
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()
    board.graphics = None
    api = LazerBikeAPI(LazerBikeCore(board))
    b1 = Bike(200, 1, max_trace=-1, graphics=False)
    b1.turn(GO_RIGHT)
    api.game.addUnit(b1, 1, (2, 2))
    b2 = Bike(200, 2, max_trace=-1, graphics=False)
    b2.turn(GO_LEFT)
    api.game.addUnit(b2, 2, (17, 17))
    api.performMove(1, GO_RIGHT)
    api.performMove(2, GO_LEFT)
    controllers = [RandomBot(1), RandomBot(2)]
    benchmark = Benchmark(api, controllers)
    print(benchmark.benchmark(5))




