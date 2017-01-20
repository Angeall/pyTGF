from abc import ABCMeta

from controls.events.human import HumanEvent
from controls.linker import Linker


class HumanLinker(Linker, metaclass=ABCMeta):
    @property
    def typeOfEventFromGame(self):
        return HumanEvent
