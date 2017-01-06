from functools import partial

from copy import deepcopy

from board.boards.square_board import SquareBoard
from board.tile import Tile
from characters.moves.continous import ContinuousMove
from characters.moves.path import Path
from examples.lazerbike.controls.allowed_moves import *
from examples.lazerbike.units.bike import Bike
from examples.lazerbike.units.trace import Trace
from game.game import Game, UnfeasibleMoveException
from game.mainloop import MAX_FPS


class LazerBikeGame(Game):
    def __init__(self, board: SquareBoard):
        super().__init__(board)
        self._unitsPreviousMoves = {}
        self._previousTraces = {}

    def createMoveForEvent(self, unit: Bike, event, max_moves: int=-1) -> Path:
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
            return ContinuousMove(unit, self.getTileForUnit, fct, MAX_FPS, pre_action=pre_action, max_moves=max_moves,
                                  step_post_action=partial(self._letTraceOnPreviousTile, unit=unit))
        raise UnfeasibleMoveException("The event couldn't create a valid move")

    def _letTraceOnPreviousTile(self, unit: Bike, previous_tile: Tile, current_tile: Tile):
        # TODO: continuous line using center-to-center trace but need previous_previous_tile
        tile_to_place_trace = previous_tile
        trace = Trace(unit.playerNumber)
        if tile_to_place_trace.graphics is not None:
            self._resizeTrace(trace, tile_to_place_trace)
            trace.moveTo(tile_to_place_trace.graphics.center)
        self._previousTraces[unit] = trace
        tile_to_place_trace.addOccupant(trace)
        unit.addParticle(trace)

    @staticmethod
    def _resizeTrace(trace, current_tile: Tile):
        if current_tile.graphics is not None:
            width = int(round(current_tile.graphics.sideLength / 2))
            height = int(round(current_tile.graphics.sideLength / 2))
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

    # def _copyGame(self, game):
    #     super()._copyGame(game)
    #     self._unitsPreviousMoves = deepcopy(game._unitsPreviousMoves)
    #     self._previousTraces = deepcopy(game._previousTraces)
