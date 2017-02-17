"""
File containing the definition of an abstract Human Controller
"""

from abc import ABCMeta, abstractmethod
from typing import List

from pytgf.characters.moves import MoveDescriptor
from pytgf.controls.controllers.controller import Controller
from pytgf.controls.events import HumanEvent, KeyboardEvent, MouseEvent

__author__ = 'Anthony Rouneau'


class Human(Controller, metaclass=ABCMeta):
    """
    An abstract definition of a Human Controller, reacting to keyboard and mouse events
    """

    def reactToEvents(self, events: List[HumanEvent]) -> MoveDescriptor:
        """
        The human controller reacts to human input => keyboard or mouse (joypad controller could be added)

        Args:
            events: The list of input event
        """
        res = None
        for event in events:
            if isinstance(event, MouseEvent):
                res = self.reactToMouseEvent(event)
            elif isinstance(event, KeyboardEvent):
                res = self.reactToKeyboardEvent(event)
        if res is not None:
            self.moves.put(res)

    @abstractmethod
    def reactToKeyboardEvent(self, keyboard_event: KeyboardEvent) -> MoveDescriptor:
        """
        Makes the controller react to an input. (e.g. input_key == K_RIGHT: self.moves.put(Move(right=True)) )

        Args:
            keyboard_event: The key board event to handle
        """
        pass

    @abstractmethod
    def reactToMouseEvent(self, mouse_event: MouseEvent) -> MoveDescriptor:
        """
        Reacts to a click
        Args:
            mouse_event: The mouse event to handle
        """
        pass
