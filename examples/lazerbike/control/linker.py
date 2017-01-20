from abc import ABCMeta

from controls.linker import Linker
from controls.linkers.bot import BotLinker
from controls.linkers.human import HumanLinker

# The order respects the trigonometrical circle right =0*pi/2, up = pi/2, ...
GO_RIGHT = 0
GO_UP = 1
GO_LEFT = 2
GO_DOWN = 3


class LazerBikeLinker(Linker, metaclass=ABCMeta):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return type(move_descriptor) == int and 0 <= move_descriptor <= 3


class LazerBikeHumanLinker(HumanLinker, LazerBikeLinker):
    pass


class LazerBikeBotLinker(BotLinker, LazerBikeLinker):
    pass
