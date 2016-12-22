from characters.controllers.human import Human
from examples.sokoban.controls.player import SokobanPlayer


class HumanPlayer(SokobanPlayer, Human):
    def __init__(self, player_number: int, right_key: int, left_key: int, up_key: int, down_key: int):
        super().__init__(player_number)
        self.rightKey = right_key
        self.leftKey = left_key
        self.upKey = up_key
        self.downKey = down_key

    def reactToTileClicked(self, tile_id, mouse_state=(True, False, False), click_up=False, **game_info: ...) -> None:
        if mouse_state[0]:
            self.goToTile(tile_id)

    def reactToInput(self, input_key: int, **game_info: ...) -> None:
        if "player_tile" in game_info:
            player_tile = game_info["player_tile"]
            new_tile_id = None
            if input_key == self.rightKey:
                new_tile_id = (player_tile[0], player_tile[1] + 1)
            elif input_key == self.leftKey:
                new_tile_id = (player_tile[0], player_tile[1] - 1)
            elif input_key == self.upKey:
                new_tile_id = (player_tile[0] - 1, player_tile[1])
            elif input_key == self.downKey:
                new_tile_id = (player_tile[0] + 1, player_tile[1])
            if new_tile_id is not None:
                self.goToTile(new_tile_id)
