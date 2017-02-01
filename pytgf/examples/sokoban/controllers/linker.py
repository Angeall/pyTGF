from abc import ABCMeta

from controls.linker import Linker
from controls.linkers.human import HumanLinker

from pytgf.controls.linkers.bot import BotLinker


class SokobanLinker(Linker, metaclass=ABCMeta):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return True


class SokobanHumanLinker(HumanLinker, SokobanLinker):
    pass


class SokobanBotLinker(BotLinker, SokobanLinker):
    pass
