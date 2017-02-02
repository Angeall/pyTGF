"""
File containing the definition of a Linker that links the game with a human controller
"""

from abc import ABCMeta

from pytgf.controls.events.human import HumanEvent
from pytgf.controls.linkers.linker import Linker

__author__ = 'Anthony Rouneau'


class HumanLinker(Linker, metaclass=ABCMeta):
    """
    Linker between the game and a human controller
    """
    @property
    def typeOfEventFromGame(self) -> type:
        """
        Returns: The type of event that will be receive from the game : HumanEvent
        """
        return HumanEvent
