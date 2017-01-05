from characters.controllers.bot import Bot
from examples.lazerbike.controls.player import LazerBikePlayer


class BotTest(LazerBikePlayer, Bot):
    def __init__(self, player_number):
        """
        Instantiates a bot controller (that does nothing) for a unit.
        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)

    def _reactToNewGameState(self, game_state) -> None:
        pass

    def _isGameStateAlreadyHandled(self, game_state) -> bool:
        pass
