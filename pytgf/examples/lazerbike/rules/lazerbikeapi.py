"""
File containing the definition of the API used by the bot controllers of the Lazerbike game
"""
from functools import partial
from typing import List

from pytgf.board import Tile, TileIdentifier
from pytgf.characters.moves import ContinuousPath
from pytgf.characters.moves import Path
from pytgf.examples.lazerbike.gamedata import MAX_FPS, GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT
from pytgf.examples.lazerbike.rules.lazerbike import LazerBikeCore
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.examples.lazerbike.units.trace import Trace
from pytgf.game import API, UnfeasibleMoveException


class LazerBikeAPI(API):
    """
    Defines the API with which the controllers can communicate
    """

    def __init__(self, game: LazerBikeCore):
        super().__init__(game)
        self._unitsPreviousMoves = {}
        self._previousTraces = {}

    def createMoveForDescriptor(self, unit: Bike, move_descriptor, max_moves: int=-1, force=False) -> Path:
        fct = None
        pre_action = None
        initial_move = unit not in self._unitsPreviousMoves.keys() or force
        if move_descriptor == GO_RIGHT:
            if initial_move or (unit.currentAction != GO_LEFT):
                pre_action = partial(unit.turn, GO_RIGHT)
                fct = self.game.getRightTile
        elif move_descriptor == GO_LEFT:
            if initial_move or (unit.currentAction != GO_RIGHT):
                pre_action = partial(unit.turn, GO_LEFT)
                fct = self.game.getLeftTile
        elif move_descriptor == GO_DOWN:
            if initial_move or (unit.currentAction != GO_UP):
                pre_action = partial(unit.turn, GO_DOWN)
                fct = self.game.getBottomTile
        elif move_descriptor == GO_UP:
            if initial_move or (unit.currentAction != GO_DOWN):
                pre_action = partial(unit.turn, GO_UP)
                fct = self.game.getTopTile
        if fct is not None:
            if initial_move:
                self._unitsPreviousMoves[unit] = move_descriptor
            return ContinuousPath(unit, self.game.getTileForUnit, fct, MAX_FPS, pre_action=pre_action,
                                  max_moves=max_moves, step_post_action=partial(self._letTraceOnPreviousTile,
                                                                                unit=unit),
                                  units_location_dict=self.game.unitsLocation)
        raise UnfeasibleMoveException("The event couldn't create a valid move")

    def _resizeTrace(self, trace, current_tile: Tile) -> None:
        """
        Resize the trace so that it does not exceed the tile's size

        Args:
            trace: The trace to resize
            current_tile: The
        """
        if self.game.board.graphics is not None:
            width = int(round(self.game.board.graphics.sideLength / 2))
            height = int(round(self.game.board.graphics.sideLength / 2))
            trace.sprite.size(width, height)

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
        if self.game.board.graphics is not None:
            self._resizeTrace(trace, self.game.board)
            trace.moveTo(tile_to_place_trace.center)
        self._previousTraces[unit] = trace
        self.game.addUnitToTile(tile_to_place_trace.identifier, trace)
        unit.addParticle(trace)

    def isWall(self, tile_id: TileIdentifier) -> bool:
        """
        Args:
            tile_id: The (i, j) coordinates of the tile. i being the row index and j being the column index.

        Returns: True if the tile located at the given ID is a wall, False otherwise
        """
        return self.game.board.getTileById(tile_id) is self.game.board.OUT_OF_BOARD_TILE

    def getDeadlyTiles(self) -> List[TileIdentifier]:
        """
        Returns: A list containing the identifier of every tiles that are deadly for the given player.
        """
        deadly_tiles = []
        for player_number in self.getPlayerNumbers():
            player = self.game.players[player_number]
            deadly_tiles.append(self.game.unitsLocation[player])
            for player_particle in player.getParticles():
                deadly_tiles.append(self.game.unitsLocation[player_particle])
        return deadly_tiles

    def getSafeAdjacentTiles(self, tile_id: TileIdentifier) -> List[TileIdentifier]:
        """

        Args:
            tile_id: The (i, j) coordinates of the tile. i being the row index and j being the column index.

        Returns: The list of each identifier of the adjacent tiles of the given tile that are safe.
        """
        adjacent_safe_tiles = []
        for adjacent_tile_id in self.getAdjacent(tile_id):
            if self.isTileSafe(adjacent_tile_id):
                adjacent_safe_tiles.append(adjacent_tile_id)
        return adjacent_safe_tiles

    def isTileSafe(self, tile_id: TileIdentifier) -> bool:
        """
        Args:
            tile_id: The (i, j) coordinates of the tile. i being the row index and j being the column index.

        Returns: True if the tile is safe for the player
        """
        return not self.isWall(tile_id) and tile_id not in self.getDeadlyTiles()

    def getLeftTileId(self, origin_tile_id: TileIdentifier) -> TileIdentifier:
        """
        Get the tile left to the given tile
        Args:
            origin_tile_id: The tile from which we want its left tile

        Returns: The tile located to the left of the given tile
        """
        return self.game.board.getTileById((origin_tile_id[0], origin_tile_id[1] - 1))

    def getRightTileId(self, origin_tile_id: TileIdentifier) -> TileIdentifier:
        """
        Get the tile right to the given tile
        Args:
            origin_tile_id: The tile from which we want its right tile

        Returns: The tile located to the right of the given tile
        """
        return self.game.board.getTileById((origin_tile_id[0], origin_tile_id[1] + 1))

    def getTopTileId(self, origin_tile_id: TileIdentifier) -> TileIdentifier:
        """
        Get the tile top to the given tile
        Args:
            origin_tile_id: The tile from which we want its top tile

        Returns: The tile located to the top of the given tile
        """
        return self.game.board.getTileById((origin_tile_id[0] - 1, origin_tile_id[1]))

    def getBottomTileId(self, origin_tile_id: TileIdentifier) -> TileIdentifier:
        """
        Get the tile bottom to the given tile
        Args:
            origin_tile_id: The tile from which we want its bottom tile

        Returns: The tile located to the bottom of the given tile
        """
        return self.game.board.getTileById((origin_tile_id[0] + 1, origin_tile_id[1]))
