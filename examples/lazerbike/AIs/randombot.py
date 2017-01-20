import random
import time

from controls.controllers.bot import Bot
from examples.lazerbike.control.player import LazerBikePlayer
from game.gamestate import GameState


class RandomBot(LazerBikePlayer, Bot):
    def __init__(self, player_number):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self.availableMoves = [self.goDown, self.goLeft, self.goRight, self.goUp]
        self._playersMove = []

    def _selectNewMove(self, game_state: GameState) -> None:
        for i in range(30):
            b = GameState(game_state.game.copy())
        random_move = random.choice(self.availableMoves)
        random_move()

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        self._playersMove.append(player_number)
        if len(self._playersMove) >= self.gameState.getNumberOfAlivePlayers():
            self._playersMove = []
            return True
        else:
            return False
