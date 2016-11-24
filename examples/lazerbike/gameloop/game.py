from characters.controllers.human import Human
from characters.controller import Controller
from characters.moves.continous import ContinuousMove
from examples.lazerbike.controllers.allowed_moves import *
from examples.lazerbike.sprites.bike import Bike
from display.tile import Tile
from display.boards.square_board import SquareBoard
from loop.game import Game, MAX_FPS


class LazerBikeGame(Game):
    def _handleControllerEvent(self, controller: Controller, event) -> None:
        unit = self._getUnitFromController(controller)  # type: Bike
        board = self.board  # type: SquareBoard
        fct = None
        print('got event: ' + str(event))
        if event == GO_RIGHT:
            if unit.direction != GO_LEFT:
                unit.turn(GO_RIGHT)
                fct = board.getRightTile
        elif event == GO_LEFT:
            if unit.direction != GO_RIGHT:
                unit.turn(GO_LEFT)
                fct = board.getLeftTile
        elif event == GO_DOWN:
            if unit.direction != GO_UP:
                unit.turn(GO_DOWN)
                fct = board.getBottomTile
        elif event == GO_UP:
            if unit.direction != GO_DOWN:
                unit.turn(GO_UP)
                fct = board.getTopTile
        if fct is not None:
            self._addMove(controller, ContinuousMove(unit, self._getTileForUnit, fct, MAX_FPS))

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple, click_up: bool):
        pass

    def _sendInputToHumanController(self, controller: Human, input_key: int):
        print('event received: ', str(input_key))
        controller.reactToInput(input_key)
