from abc import ABCMeta

from controls.controller import Controller
from controls.controllers.bot import Bot
from examples.lazerbike.control.api import LazerBikeGameState, GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN

from pytgf.game.game import Game


class LazerBikePlayer(Controller, metaclass=ABCMeta):
    def __init__(self, player_number):
        super().__init__(player_number)

    def goLeft(self):
        self.moves.put(GO_LEFT)

    def goRight(self):
        self.moves.put(GO_RIGHT)

    def goUp(self):
        self.moves.put(GO_UP)

    def goDown(self):
        self.moves.put(GO_DOWN)


class LazerBikeBotPlayer(LazerBikePlayer, Bot, metaclass=ABCMeta):
    def __init__(self, player_number):
        """
        Instantiates an abstract bot controller that is meant to play the lazerbike game

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self.availableMoves = [GO_DOWN, GO_UP, GO_RIGHT, GO_LEFT]
        self._playersMove = []

    def _getGameStateAPI(self, game: Game) -> LazerBikeGameState:
        return LazerBikeGameState(game)

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        self._playersMove.append(player_number)
        if len(self._playersMove) >= self.gameState.getNumberOfAlivePlayers():
            self._playersMove = []
            return True
        else:
            return False

    def _isMoveAllowed(self, move):
        return move in (GO_RIGHT, GO_DOWN, GO_LEFT, GO_UP)
