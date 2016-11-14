
from display.tile import Tile
from pygame.locals import *

from loop.game import Game


class LazerBikeGame(Game):
    def _onKeyPressed(self, key_id: int) -> None:
        if key_id == K_RIGHT:
            self.board.units[0].moveRight(1)
        elif key_id == K_LEFT:
            self.board.units[0].moveLeft(1)
        elif key_id == K_UP:
            self.board.units[0].moveUp(1)
        elif key_id == K_DOWN:
            self.board.units[0].moveDown(1)

    def _onTileClickedDown(self, tile: Tile, mouse_buttons_state: tuple) -> None:
        pass

    def _onTileClickedUp(self, tile: Tile) -> None:
        pass

