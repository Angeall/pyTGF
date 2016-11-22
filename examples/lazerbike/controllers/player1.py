from pygame.locals import *

from characters.controllers.human import Human
from examples.lazerbike.controllers.allowed_moves import *


class Player1(Human):
    def reactToInput(self, input_key, *game_info: ...) -> None:
            if input_key == K_RIGHT:
                self.moves.put(GO_RIGHT)
            elif input_key == K_LEFT:
                self.moves.put(GO_LEFT)
            elif input_key == K_UP:
                self.moves.put(GO_UP)
            elif input_key == K_DOWN:
                self.moves.put(GO_DOWN)

    def reactToTileClicked(self, tile=None, mouse_state=(False, False, False), click_up=False, *game_info) -> None:
        pass
