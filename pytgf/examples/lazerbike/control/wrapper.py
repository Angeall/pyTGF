"""
Defines a specific controller wrapper for the Lazerbike game.
"""

from abc import ABCMeta

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.wrappers import ControllerWrapper, HumanControllerWrapper, BotControllerWrapper


class LazerBikeControllerWrapper(ControllerWrapper, metaclass=ABCMeta):
    """
    Defines a specific controller wrapper for the Lazerbike Game, in which the move descriptor is an int
    between 0 and 3 (see file constants).
    """
    def isMoveDescriptorAllowed(self, move_descriptor: MoveDescriptor) -> bool:
        return type(move_descriptor) == int and 0 <= move_descriptor <= 3


class LazerBikeHumanControllerWrapper(HumanControllerWrapper, LazerBikeControllerWrapper):
    """
    The human controller wrapper for the lazerbike game
    """
    pass


class LazerBikeBotControllerWrapper(BotControllerWrapper, LazerBikeControllerWrapper):
    """
    The bot controller wrapper for the lazerbike game
    """
    pass
