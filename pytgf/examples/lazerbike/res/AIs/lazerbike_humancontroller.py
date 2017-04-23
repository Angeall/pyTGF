"""
File containing the definition of a human player for the Lazerbike Game
"""
from ...control.player import LazerBikePlayer
from ...gamedata import GO_LEFT, GO_RIGHT, GO_UP, GO_DOWN
from .....controls.controllers import Human
from .....controls.events import KeyboardEvent, MouseEvent


class HumanPlayer(LazerBikePlayer, Human):
    """
    Defines a human player for the Lazerbike game
    """

    def __init__(self, player_number: int, right_key: int, left_key: int, up_key: int, down_key: int):
        """
        Instantiates the human controller

        Args:
            player_number: The number of the player controlled by this controller
            right_key: The key to press to go right
            left_key: The key to press to go left
            up_key: The key to press to gop up
            down_key: The key to press to go down
        """
        super().__init__(player_number)
        self.rightKey = right_key
        self.leftKey = left_key
        self.upKey = up_key
        self.downKey = down_key

    def reactToKeyboardEvent(self, keyboard_event: KeyboardEvent) -> None:
        """
        Reacts when the player receives a keyboard event

        Args:
            keyboard_event: The keyboard event received
        """
        return_key = None
        for input_key in keyboard_event.characterKeys:
            if input_key == self.rightKey:
                return_key = GO_RIGHT
            elif input_key == self.leftKey:
                return_key = GO_LEFT
            elif input_key == self.upKey:
                return_key = GO_UP
            elif input_key == self.downKey:
                return_key = GO_DOWN
        return return_key

    def reactToMouseEvent(self, mouse_event: MouseEvent) -> None:
        """
        Does nothing if it receives a mouse event...

        Args:
            mouse_event: The mouse event received
        """
        pass


