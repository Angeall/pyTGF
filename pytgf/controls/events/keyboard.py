"""
File containing the definition of a Keyboard Event, to send to Human Controllers
"""
from typing import Tuple

from ..events import HumanEvent

__author__ = 'Anthony Rouneau'


class KeyboardEvent(HumanEvent):
    """
    Defines a keyboard event, with the pressed character
    """

    def __init__(self, character_keys: Tuple):
        """
        Instantiates a new keyboard event, which consists in the character keys that the user pressed

        Args:
            character_keys: The keys pressed by the user
        """
        self.characterKeys = character_keys  # type: tuple
