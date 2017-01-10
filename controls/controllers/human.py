from abc import ABCMeta, abstractmethod

from controls.controller import Controller
from controls.events.human import HumanEvent
from controls.events.keyboard import KeyboardEvent
from controls.events.mouse import MouseEvent


class Human(Controller, metaclass=ABCMeta):

    def reactToEvent(self, event: HumanEvent):
        """
        The human controller reacts to human input => keyboard or mouse (joypad controller could be added)

        Args:
            event: The input event
        """
        if isinstance(event, MouseEvent):
            self.reactToMouseEvent(event)
        elif isinstance(event, KeyboardEvent):
            self.reactToKeyboardEvent(event)

    @abstractmethod
    def reactToKeyboardEvent(self, keyboard_event: KeyboardEvent) -> None:
        """
        Makes the controller react to an input. (e.g. input_key == K_RIGHT: self.moves.put(Move(right=True)) )

        Args:
            keyboard_event: The key board event to handle
        """
        pass

    @abstractmethod
    def reactToMouseEvent(self, mouse_event: MouseEvent) -> None:
        """
        Reacts to a click
        Args:
            mouse_event: The mouse event to handle
        """
        pass
