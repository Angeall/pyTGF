from characters.controllers.human import Human
from characters.controller import Controller
from examples.lazerbike.controllers.allowed_moves import *
from display.tile import Tile
from loop.game import Game


class LazerBikeGame(Game):
    def _handleControllerEvent(self, controller: Controller, event) -> None:
        unit = self._controllers[controller]
        if event == GO_RIGHT:

        elif event == GO_RIGHT:

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple, click_up: bool):
        pass

    def _sendInputToHumanController(self, controller: Human, input_key: int):
        controller.reactToInput(input_key)
