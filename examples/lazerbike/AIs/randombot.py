import random

from characters.controllers.bot import Bot
from examples.lazerbike.controls.player import LazerBikePlayer
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

    def _reactToNewGameState(self, game_state: GameState) -> None:
        random_move = random.choice(self.availableMoves)
        random_move()

    def _isGameStateAlreadyHandled(self, game_state: GameState) -> bool:
        return False
