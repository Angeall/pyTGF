from abc import ABCMeta

from pytgf.controls import HumanEvent
from pytgf.controls import Linker


class HumanLinker(Linker, metaclass=ABCMeta):
    @property
    def typeOfEventFromGame(self):
        return HumanEvent
