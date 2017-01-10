from controls.controllers.human import Human
from controls.events.mouse import MouseEvent
from examples.sokoban.controllers.player import SokobanPlayer
from examples.sokoban.rules.game import SokobanKeyboardEvent


class HumanPlayer(SokobanPlayer, Human):
    def __init__(self, player_number: int, right_key: int, left_key: int, up_key: int, down_key: int):
        super().__init__(player_number)
        self.rightKey = right_key
        self.leftKey = left_key
        self.upKey = up_key
        self.downKey = down_key

    def reactToMouseEvent(self, mouse_event: MouseEvent) -> None:
        if mouse_event.mouseState[0]:
            if mouse_event.tileId is not None:
                self.goToTile(mouse_event.tileId)

    def reactToKeyboardEvent(self, keyboard_event: SokobanKeyboardEvent) -> None:
        player_tile_id = keyboard_event.playerTileID
        input_key = keyboard_event.characterKeys[0]
        new_tile_id = None
        if input_key == self.rightKey:
            new_tile_id = (player_tile_id[0], player_tile_id[1] + 1)
        elif input_key == self.leftKey:
            new_tile_id = (player_tile_id[0], player_tile_id[1] - 1)
        elif input_key == self.upKey:
            new_tile_id = (player_tile_id[0] - 1, player_tile_id[1])
        elif input_key == self.downKey:
            new_tile_id = (player_tile_id[0] + 1, player_tile_id[1])
        if new_tile_id is not None:
            self.goToTile(new_tile_id)
