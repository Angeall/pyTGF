from characters.controllers.bot import Bot
from examples.lazerbike.controls.player import LazerBikePlayer


class BotTest(LazerBikePlayer, Bot):
    def __init__(self, player_number):
        super().__init__(player_number)

    def _reactToNewGameState(self, game_state) -> None:
        pass

    def _isGameStateHandled(self, game_state) -> bool:
        pass
