"""
File containing the definition of a ControllerWrapper that links the game with a human controller
"""

from abc import ABCMeta

from pytgf.controls.events.human import HumanEvent
from pytgf.controls.wrappers.wrapper import ControllerWrapper

__author__ = 'Anthony Rouneau'


class HumanControllerWrapper(ControllerWrapper, metaclass=ABCMeta):
    """
    ControllerWrapper between the game and a human controller
    """
    @property
    def typeOfEventFromGame(self) -> type:
        """
        Returns: The type of event that will be receive from the game : HumanEvent
        """
        return HumanEvent
