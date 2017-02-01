import random

from pytgf.examples.lazerbike.control.player import LazerBikeBotPlayer
from pytgf.game.gamestate import GameState


class RandomBot(LazerBikeBotPlayer):
    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def __init__(self, player_number):
        """
        Instantiates a bot controller that choose its new move randomly for its unit.

        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)
        self._playersMove = []

    def _selectNewMove(self, game_state: GameState) -> None:
        random_move = random.choice(self.availableMoves)
        random_move()
