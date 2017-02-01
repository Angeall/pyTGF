from controls.event import Event

from pytgf.controls.controllers import Bot


class PassiveController(Bot):
    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def _isMoveAllowed(self, move) -> bool:
        return False

    def _getGameStateAPI(self, game):
        return None

    def _selectNewMove(self, game_state):
        pass

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        pass

    def reactToEvents(self, events: Event):
        pass
