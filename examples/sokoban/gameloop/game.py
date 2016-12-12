from loop.game import Game
from characters.controller import Controller
from characters.controllers.human import Human
from display.tile import Tile


class SokobanGame(Game):
    def _sendInputToHumanController(self, controller: Human, input_key: int) -> None:
        pass

    def _isFinished(self) -> (bool, list):
        pass

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple,
                                         click_up: bool) -> None:
        pass

    def _handleControllerEvent(self, controller: Controller, event) -> None:
        pass
