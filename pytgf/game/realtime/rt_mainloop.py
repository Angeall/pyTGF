from typing import List

from ..mainloop import MainLoop
from ...characters.moves import MoveDescriptor
from ...characters.units import Unit
from ...controls.wrappers import ControllerWrapper


class RealTimeMainLoop(MainLoop):
    def _reactToFinishedMove(self):
        pass

    def _getPlayerNumbersToWhichSendEvents(self) -> List[int]:
        return self.api.getPlayerNumbers()

    def _mustRetrieveNextMove(self, current_wrapper: ControllerWrapper) -> bool:
        # TODO -- LAP !
        return True

    def _mustSendInitialWakeEvent(self, initial_action: MoveDescriptor, unit: Unit) -> bool:
        return initial_action is None
