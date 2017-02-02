"""
Defines a specific linker for the Lazerbike game.
"""

from abc import ABCMeta

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.linkers import Linker, HumanLinker, BotLinker

# The order respects the trigonometrical circle right =0*pi/2, up = pi/2, ...
GO_RIGHT = 0
GO_UP = 1
GO_LEFT = 2
GO_DOWN = 3


class LazerBikeLinker(Linker, metaclass=ABCMeta):
    """
    Defines a specific linker for the Lazerbike Game, in which the move descriptor is an int
    between 0 and 3 (see file constants).
    """
    def isMoveDescriptorAllowed(self, move_descriptor: MoveDescriptor) -> bool:
        return type(move_descriptor) == int and 0 <= move_descriptor <= 3


class LazerBikeHumanLinker(HumanLinker, LazerBikeLinker):
    """
    The human linker for the lazerbike game
    """
    pass


class LazerBikeBotLinker(BotLinker, LazerBikeLinker):
    """
    The bot linker for the lazerbike game
    """
    pass
