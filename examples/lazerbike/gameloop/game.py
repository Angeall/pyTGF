from characters.controllers.human import Human
from characters.controller import Controller
from characters.moves.continous import ContinuousMove
from examples.lazerbike.controls.allowed_moves import *
from examples.lazerbike.sprites.bike import Bike
from examples.lazerbike.sprites.trace import Trace
from display.tile import Tile
from display.boards.square_board import SquareBoard
from loop.game import Game, MAX_FPS
from functools import partial
from types import FunctionType as function


class LazerBikeGame(Game):
    def __init__(self, board: SquareBoard):
        super().__init__(board)
        self._unitsPreviousMoves = {}
        self._previousTraces = {}
        self.setSuicide(True)

    def _handleGameFinished(self, winning_units: list):
        if winning_units is None:
            return "DRAW"
        else:
            msg = "WON: "
            for player in winning_units:
                msg += "Player " + str(player.playerNumber) + ", "
            msg = msg[:-2]
            return msg

    def _isFinished(self) -> (bool, list):
        teams_alive = 0
        team_units = []
        for team in self._teams.values():
            for unit in team:
                if unit.isAlive():
                    teams_alive += 1
                    team_units = team
                    break
        if teams_alive > 1:
            return False, None
        elif teams_alive == 0:
            return True, None
        else:
            return True, team_units

    def _handleControllerEvent(self, controller: Controller, event) -> None:
        unit = self._getUnitFromController(controller)  # type: Bike
        board = self.board  # type: SquareBoard
        fct = None
        pre_action = None
        initial_move = unit not in self._unitsPreviousMoves.keys()
        if event == GO_RIGHT:
            if initial_move or (unit.direction != GO_LEFT and unit.direction != GO_RIGHT):
                pre_action = partial(unit.turn, GO_RIGHT)
                fct = board.getRightTile
        elif event == GO_LEFT:
            if initial_move or (unit.direction != GO_RIGHT and unit.direction != GO_LEFT):
                pre_action = partial(unit.turn, GO_LEFT)
                fct = board.getLeftTile
        elif event == GO_DOWN:
            if initial_move or (unit.direction != GO_UP and unit.direction != GO_DOWN):
                pre_action = partial(unit.turn, GO_DOWN)
                fct = board.getBottomTile
        elif event == GO_UP:
            if initial_move or (unit.direction != GO_DOWN and unit.direction != GO_UP):
                pre_action = partial(unit.turn, GO_UP)
                fct = board.getTopTile
        if fct is not None:
            if initial_move:
                self._unitsPreviousMoves[unit] = event
            self._addMove(controller, ContinuousMove(unit, self._getTileForUnit, fct, MAX_FPS,
                                                     pre_action=pre_action,
                                                     step_post_action=partial(self._letTraceOnPreviousTile, unit=unit)))

    def _letTraceOnPreviousTile(self, unit: Bike, previous_tile: Tile, current_tile: Tile):
        tile_to_place_trace = previous_tile
        trace = Trace(unit.playerNumber)
        self._resizeTrace(trace, tile_to_place_trace)
        trace.moveTo(tile_to_place_trace.center)
        self._previousTraces[unit] = trace
        tile_to_place_trace.addOccupant(trace)
        unit.addParticle(trace)

    @staticmethod
    def _resizeTrace(trace, current_tile):
        width = int(round(current_tile.sideLength / 2))
        height = int(round(current_tile.sideLength / 2))
        trace.sprite.size(width, height)

    @staticmethod
    def _determineCurrentDirection(previous_tile: Tile, current_tile: Tile) -> int:
        if previous_tile.identifier[1] == current_tile.identifier[1]:  # Vertical movement
            if previous_tile.identifier[0] > current_tile.identifier[0]:
                return GO_UP
            else:
                return GO_DOWN
        else:  # Horizontal movement
            if previous_tile.identifier[1] > current_tile.identifier[1]:
                return GO_LEFT
            else:
                return GO_RIGHT

    @staticmethod
    def _isMovementVertical(previous_tile: Tile, current_tile: Tile) -> bool:
        return previous_tile.identifier[1] - current_tile.identifier[1] == 0

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple, click_up: bool):
        pass

    def _sendInputToHumanController(self, controller: Human, input_key: int):
        controller.reactToInput(input_key)
