"""
File containing the definition of a testing controller that does nothing
"""

from pytgf.controls.controllers.bot import Bot
from pytgf.controls.events import Event

__author__ = 'Anthony Rouneau'


class Passive(Bot):
    """
    Controller that does literally nothing. Used for testing purpose
    """

    def selectMoveFollowingTeammateMessage(self, teammate_number: int, message):
        pass

    def _isMoveAllowed(self, move_descriptor) -> bool:
        return False

    def _getGameStateAPI(self, game):
        return None

    def _selectNewMove(self, game_state):
        pass

    def _isMoveInteresting(self, player_number: int, new_move_event) -> bool:
        pass

    def reactToEvents(self, events: Event):
        pass
