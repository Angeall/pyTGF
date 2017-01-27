from examples.lazerbike.control.player import LazerBikeBotPlayer


class BotTest(LazerBikeBotPlayer):
    def __init__(self, player_number):
        """
        Instantiates a bot controller (that does nothing) for a unit.
        Args:
            player_number: The identifier of the unit controlled by this controller
        """
        super().__init__(player_number)

    def _selectNewMove(self, game_state) -> None:
        pass

    def _isMoveInteresting(self, player_number, new_move_event) -> bool:
        return False
