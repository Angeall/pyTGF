from controls.controllers.bot import Bot
from controls.event import Event


class PassiveController(Bot):
    def _getGameStateAPI(self, game):
        return None

    def _selectNewMove(self, game_state):
        pass

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        pass

    def reactToEvents(self, events: Event):
        pass
