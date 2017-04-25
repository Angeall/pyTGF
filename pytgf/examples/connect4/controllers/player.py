from abc import ABCMeta

from ....characters.moves import MoveDescriptor
from ....controls.controllers import Bot
from ....controls.controllers import Controller
from ....examples.connect4.rules import Connect4API, Connect4Core
from ....game.turnbased import TurnBasedAPI

__author__ = "Anthony Rouneau"


class Connect4Player(Controller, metaclass=ABCMeta):
    pass


class Connect4BotPlayer(Connect4Player, Bot, metaclass=ABCMeta):
    @property
    def possibleMoves(self):
        return list(range(7))

    def _isMoveAllowed(self, move_descriptor: MoveDescriptor):
        return move_descriptor in self.possibleMoves

    def _isMoveInteresting(self, player_number: int, new_move_event: MoveDescriptor):
        game_state = self.gameState  # type: TurnBasedAPI
        return game_state.isCurrentPlayer(self.playerNumber)

    def _getGameStateAPI(self, game: Connect4Core):
        return Connect4API(game)