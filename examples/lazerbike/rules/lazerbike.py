from functools import partial

from copy import deepcopy

from gameboard.boards.square_board import SquareBoard
from gameboard.tile import Tile
from characters.moves.continous import ContinuousMove
from characters.moves.path import Path
from examples.lazerbike.control.linker import GO_RIGHT, GO_LEFT, GO_DOWN, GO_UP
from examples.lazerbike.units.bike import Bike
from examples.lazerbike.units.trace import Trace
from game.game import Game, UnfeasibleMoveException
from game.mainloop import MAX_FPS


class LazerBikeGame(Game):
    @property
    def _suicideAllowed(self) -> bool:
        return True

    @property
    def _teamKillAllowed(self) -> bool:
        return True

    def __init__(self, board: SquareBoard):
        super().__init__(board)
        self._unitsPreviousMoves = {}
        self._previousTraces = {}

    def createMoveForDescriptor(self, unit: Bike, move_descriptor, max_moves: int=-1, force=False) -> Path:
        board = self.board  # type: SquareBoard
        fct = None
        pre_action = None
        initial_move = unit not in self._unitsPreviousMoves.keys() or force
        if move_descriptor == GO_RIGHT:
            if initial_move or (unit.currentAction != GO_LEFT):
                pre_action = partial(unit.turn, GO_RIGHT)
                fct = board.getRightTile
        elif move_descriptor == GO_LEFT:
            if initial_move or (unit.currentAction != GO_RIGHT):
                pre_action = partial(unit.turn, GO_LEFT)
                fct = board.getLeftTile
        elif move_descriptor == GO_DOWN:
            if initial_move or (unit.currentAction != GO_UP):
                pre_action = partial(unit.turn, GO_DOWN)
                fct = board.getBottomTile
        elif move_descriptor == GO_UP:
            if initial_move or (unit.currentAction != GO_DOWN):
                pre_action = partial(unit.turn, GO_UP)
                fct = board.getTopTile
        if fct is not None:
            if initial_move:
                self._unitsPreviousMoves[unit] = move_descriptor
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

    def _collidePlayers(self, player1, player2, frontal: bool = False):
        """
        Makes what it has to be done when the first given player collides with a particle of the second given player
        (Careful : two moving units (alive units) colliding each other causes a frontal collision that hurts both
        units)

        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
        """
        return super()._collidePlayers(player1, player2, frontal)

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
