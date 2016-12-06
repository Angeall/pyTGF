from characters.controllers.human import Human
from examples.lazerbike.controls.player import LazerBikePlayer


class HumanPlayer(LazerBikePlayer, Human):
    def __init__(self, player_number: int, right_key: int, left_key: int, up_key: int, down_key: int):
        super().__init__(player_number)
        self.rightKey = right_key
        self.leftKey = left_key
        self.upKey = up_key
        self.downKey = down_key

    def reactToInput(self, input_key, *game_info: ...) -> None:
            if input_key == self.rightKey:
                self.goRight()
            elif input_key == self.leftKey:
                self.goLeft()
            elif input_key == self.upKey:
                self.goUp()
            elif input_key == self.downKey:
                self.goDown()

    def reactToTileClicked(self, tile=None, mouse_state=(False, False, False), click_up=False, *game_info) -> None:
        pass


