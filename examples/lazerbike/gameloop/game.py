from characters.controllers.human import Human
from characters.controller import Controller
from characters.moves.continous import ContinuousMove
from examples.lazerbike.controllers.allowed_moves import *
from examples.lazerbike.sprites.bike import Bike
from display.tile import Tile
from display.boards.square_board import SquareBoard
from loop.game import Game, MAX_FPS
from utils.functions import DelayedFunction


class LazerBikeGame(Game):
    def _handleControllerEvent(self, controller: Controller, event) -> None:
        unit = self._getUnitFromController(controller)  # type: Bike
        board = self.board  # type: SquareBoard
        fct = None
        pre_action = None
        if event == GO_RIGHT:
            if unit.direction != GO_LEFT:
                pre_action = DelayedFunction(unit.turn, GO_RIGHT)
                fct = board.getRightTile
        elif event == GO_LEFT:
            if unit.direction != GO_RIGHT:
                pre_action = DelayedFunction(unit.turn, GO_LEFT)
                fct = board.getLeftTile
        elif event == GO_DOWN:
            if unit.direction != GO_UP:
                pre_action = DelayedFunction(unit.turn, GO_DOWN)
                fct = board.getBottomTile
        elif event == GO_UP:
            if unit.direction != GO_DOWN:
                pre_action = DelayedFunction(unit.turn, GO_UP)
                fct = board.getTopTile
        if fct is not None:
            self._addMove(controller, ContinuousMove(unit, self._getTileForUnit, fct, MAX_FPS, pre_action=pre_action))

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple, click_up: bool):
        pass

    def _sendInputToHumanController(self, controller: Human, input_key: int):
        controller.reactToInput(input_key)
