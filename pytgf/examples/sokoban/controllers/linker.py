from abc import ABCMeta

from pytgf.controls.linkers import Linker, HumanLinker, BotLinker


class SokobanLinker(Linker, metaclass=ABCMeta):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return True


class SokobanHumanLinker(HumanLinker, SokobanLinker):
    pass


class SokobanBotLinker(BotLinker, SokobanLinker):
    pass
