from controls.controllers.human import Human
from controls.events.keyboard import KeyboardEvent
from controls.events.mouse import MouseEvent

from pytgf.examples.lazerbike.control.player import LazerBikePlayer


class HumanPlayer(LazerBikePlayer, Human):
    def __init__(self, player_number: int, right_key: int, left_key: int, up_key: int, down_key: int):
        super().__init__(player_number)
        self.rightKey = right_key
        self.leftKey = left_key
        self.upKey = up_key
        self.downKey = down_key

    def reactToKeyboardEvent(self, keyboard_event: KeyboardEvent) -> None:
        for input_key in keyboard_event.characterKeys:
            if input_key == self.rightKey:
                self.goRight()
            elif input_key == self.leftKey:
                self.goLeft()
            elif input_key == self.upKey:
                self.goUp()
            elif input_key == self.downKey:
                self.goDown()

    def reactToMouseEvent(self, mouse_event: MouseEvent) -> None:
        pass


