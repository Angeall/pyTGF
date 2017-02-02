"""
File containing the rules of the Lazerbike game
"""

from functools import partial

from pytgf.board import Board, Tile
from pytgf.characters.moves import ContinuousPath
from pytgf.characters.moves.path import Path
from pytgf.characters.units import MovingUnit
from pytgf.examples.lazerbike.control.linker import GO_RIGHT, GO_LEFT, GO_DOWN, GO_UP
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.examples.lazerbike.units.trace import Trace
from pytgf.game.game import Game, UnfeasibleMoveException
from pytgf.game.mainloop import MAX_FPS


class LazerBikeGame(Game):
    """
    Defines the rules for the Lazerbike game
    """
    @property
    def _suicideAllowed(self) -> bool:
        """
        Returns: True because a unit can suicide on its own lazer traces
        """
        return True

    @property
    def _teamKillAllowed(self) -> bool:
        """
        Returns: True because a unit can kill itself on another mate or another mate's trace...
        """
        return True

    def __init__(self, board: Board):
        """
        Instantiates a new Lazerbike game

        Args:
            board: The board that the game will use
        """
        super().__init__(board)
        self._unitsPreviousMoves = {}
        self._previousTraces = {}

    def createMoveForDescriptor(self, unit: Bike, move_descriptor, max_moves: int=-1, force=False) -> Path:
        fct = None
        pre_action = None
        initial_move = unit not in self._unitsPreviousMoves.keys() or force
        if move_descriptor == GO_RIGHT:
            if initial_move or (unit.currentAction != GO_LEFT):
                pre_action = partial(unit.turn, GO_RIGHT)
                fct = self.getRightTile
        elif move_descriptor == GO_LEFT:
            if initial_move or (unit.currentAction != GO_RIGHT):
                pre_action = partial(unit.turn, GO_LEFT)
                fct = self.getLeftTile
        elif move_descriptor == GO_DOWN:
            if initial_move or (unit.currentAction != GO_UP):
                pre_action = partial(unit.turn, GO_DOWN)
                fct = self.getBottomTile
        elif move_descriptor == GO_UP:
            if initial_move or (unit.currentAction != GO_DOWN):
                pre_action = partial(unit.turn, GO_UP)
                fct = self.getTopTile
        if fct is not None:
            if initial_move:
                self._unitsPreviousMoves[unit] = move_descriptor
            return ContinuousPath(unit, self.getTileForUnit, fct, MAX_FPS, pre_action=pre_action, max_moves=max_moves,
                                  step_post_action=partial(self._letTraceOnPreviousTile, unit=unit),
                                  units_location_dict=self.unitsLocation)
        raise UnfeasibleMoveException("The event couldn't create a valid move")

    def _letTraceOnPreviousTile(self, unit: Bike, previous_tile: Tile, current_tile: Tile) -> None:
        """
        Let a trace on the previous tile explored by the bike.

        Args:
            unit: The unit that moved from a tile to another
            previous_tile: The previous tile on which the unit was placed on
            current_tile: The current tile on which the unit is placed on
        """
        tile_to_place_trace = previous_tile
        trace = Trace(unit.playerNumber)
        if self.board.graphics is not None:
            self._resizeTrace(trace, self.board)
            trace.moveTo(tile_to_place_trace.center)
        self._previousTraces[unit] = trace
        self._addUnitToTile(tile_to_place_trace.identifier, trace)
        unit.addParticle(trace)

    def _collidePlayers(self, player1: MovingUnit, player2: MovingUnit, frontal: bool=False) -> None:
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

    def _resizeTrace(self, trace, current_tile: Tile) -> None:
        """
        Resize the trace so that it does not exceed the tile's size

        Args:
            trace: The trace to resize
            current_tile: The
        """
        if current_tile.graphics is not None:
            width = int(round(self.board.graphics.sideLength / 2))
            height = int(round(self.board.graphics.sideLength / 2))
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

    def getLeftTile(self, origin_tile: Tile) -> Tile:
        """
        Get the tile left to the given tile
        Args:
            origin_tile: The tile from which we want its left tile

        Returns: The tile located to the left of the given tile
        """
        return self.board.getTileById((origin_tile.identifier[0], origin_tile.identifier[1] - 1))

    def getRightTile(self, origin_tile: Tile) -> Tile:
        """
        Get the tile right to the given tile
        Args:
            origin_tile: The tile from which we want its right tile

        Returns: The tile located to the right of the given tile
        """
        return self.board.getTileById((origin_tile.identifier[0], origin_tile.identifier[1] + 1))

    def getTopTile(self, origin_tile: Tile) -> Tile:
        """
        Get the tile top to the given tile
        Args:
            origin_tile: The tile from which we want its top tile

        Returns: The tile located to the top of the given tile
        """
        return self.board.getTileById((origin_tile.identifier[0] - 1, origin_tile.identifier[1]))

    def getBottomTile(self, origin_tile: Tile) -> Tile:
        """
        Get the tile bottom to the given tile
        Args:
            origin_tile: The tile from which we want its bottom tile

        Returns: The tile located to the bottom of the given tile
        """
        return self.board.getTileById((origin_tile.identifier[0] + 1, origin_tile.identifier[1]))
