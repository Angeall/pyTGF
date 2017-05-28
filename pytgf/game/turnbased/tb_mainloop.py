from typing import List

from .tb_api import TurnBasedAPI
from ..mainloop import MainLoop
from ...characters.moves import MoveDescriptor
from ...characters.units import Unit
from ...controls.wrappers import ControllerWrapper


class TurnBasedMainLoop(MainLoop):

    def __init__(self, api: TurnBasedAPI):
        super().__init__(api)

    def _reactToFinishedMove(self):
        self.api.switchToNextPlayer()
        self._currentTurnTaken = False

    def _getPlayerNumbersToWhichSendEvents(self) -> List[int]:
        return [self.api.getNextPlayer()]

    def _mustRetrieveNextMove(self, current_wrapper: ControllerWrapper) -> bool:
        # TODO -- LAP !
        return self.api.isCurrentPlayer(current_wrapper.controller.playerNumber) and not self._currentTurnTaken

    def _mustSendInitialWakeEvent(self, initial_action: MoveDescriptor, unit: Unit) -> bool:
        return initial_action is None and unit.playerNumber == self.api.getCurrentPlayer()
