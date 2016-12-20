from characters.moves.listpath import ListPath
from examples.sokoban.units.box import Box
from loop.game import Game
import loop.game as game
from characters.controller import Controller
from characters.controllers.human import Human
from characters.moves.move import ImpossibleMove, ShortMove
from board.tile import Tile


class SokobanGame(Game):
    def _sendInputToHumanController(self, controller: Human, input_key: int) -> None:
        controller.reactToInput(input_key)

    def _isFinished(self) -> (bool, list):
        return False, []

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple,
                                         click_up: bool) -> None:
        controller.reactToTileClicked(tile, mouse_state, click_up)

    def _handleControllerEvent(self, controller: Controller, event) -> None:
        pass

    def _pushBoxIfNeeded(self, previous_tile: Tile, current_tile: Tile):
        box = None
        for occupant in current_tile.occupants:
            if isinstance(occupant, Box):
                box = occupant
                break
        if box is not None:
            prev_tile_id = previous_tile.identifier
            cur_tile_id = current_tile.identifier
            tile_diff = cur_tile_id[0] - prev_tile_id[0], cur_tile_id[1] - prev_tile_id[1]
            box_next_tile_id = (current_tile[0] + tile_diff[0], current_tile[1] + tile_diff[1])
            box_next_tile = self.board.getTileById(box_next_tile_id)
            if box_next_tile is self.board.OUT_OF_BOARD_TILE or not box_next_tile.walkable:
                raise ImpossibleMove("The box cannot be moved that way")
            else:
                self._addOtherMove(box, ListPath([ShortMove(box, current_tile, box_next_tile, game.MAX_FPS)]))
