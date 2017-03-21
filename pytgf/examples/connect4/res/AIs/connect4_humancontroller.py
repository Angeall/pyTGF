"""
File containing the definition of a human player for the Connect4 Game
"""
from pytgf.controls.controllers import Human
from pytgf.controls.events import KeyboardEvent, MouseEvent
from pytgf.examples.connect4.controllers.player import Connect4Player


__author__ = "Anthony Rouneau"


class HumanPlayer(Connect4Player, Human):
    """
    Defines a human player for the Connect4 game
    """

    def __init__(self, player_number: int):
        """
        Instantiates the human controller

        Args:
            player_number: The number of the player controlled by this controller
        """
        super().__init__(player_number)

    def reactToKeyboardEvent(self, keyboard_event: KeyboardEvent) -> None:
        """
        Reacts when the player receives a keyboard event

        Args:
            keyboard_event: The keyboard event received
        """
        pass

    def reactToMouseEvent(self, mouse_event: MouseEvent) -> None:
        """
        Does nothing if it receives a mouse event...

        Args:
            mouse_event: The mouse event received
        """
        if (self.playerNumber == 1 and mouse_event.mouseState[0]) or \
                (self.playerNumber == 2 and mouse_event.mouseState[2]):
            if mouse_event.tileId is not None:
                return mouse_event.tileId[1]  # The column number of the clicked tile


