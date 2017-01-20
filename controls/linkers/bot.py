from abc import ABCMeta

from controls.events.bot import BotEvent
from controls.linker import Linker


class BotLinker(Linker, metaclass=ABCMeta):
    @property
    def typeOfEventFromGame(self):
        return BotEvent
