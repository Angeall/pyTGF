from typing import List

from pytgf.characters.moves import MoveDescriptor
from pytgf.characters.units import Unit
from pytgf.controls.wrappers import ControllerWrapper
from pytgf.game.mainloop import MainLoop


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
