"""
File containing the definition of the API used by the bot controllers of the Lazerbike game
"""
from functools import partial
from typing import List

from .lazerbike import LazerBikeCore
from ..gamedata import MAX_FPS, GO_DOWN, GO_RIGHT, GO_UP, GO_LEFT
from ..units.bike import Bike
from ..units.trace import Trace
from ....board import Tile, TileIdentifier
from ....characters.moves import ContinuousPath
from ....characters.moves import MoveDescriptor
from ....characters.moves import Path
from ....game import API
from ....game import UnfeasibleMoveException


class LazerBikeAPI(API):
    """
    Defines the API with which the controllers can communicate
    """

    def __init__(self, game: LazerBikeCore):
        super().__init__(game)
        self._previousTraces = {}

    def createMoveForDescriptor(self, unit: Bike, move_descriptor, force=False, is_step: bool=False) -> Path:
        fct = None
        pre_action = None
        if move_descriptor == GO_RIGHT:
            if force or (unit.currentAction != GO_LEFT):
                pre_action = partial(unit.turn, GO_RIGHT)
                fct = self.game.getRightTile
        elif move_descriptor == GO_LEFT:
            if force or (unit.currentAction != GO_RIGHT):
                pre_action = partial(unit.turn, GO_LEFT)
                fct = self.game.getLeftTile
        elif move_descriptor == GO_DOWN:
            if force or (unit.currentAction != GO_UP):
                pre_action = partial(unit.turn, GO_DOWN)
                fct = self.game.getBottomTile
        elif move_descriptor == GO_UP:
            if force or (unit.currentAction != GO_DOWN):
                pre_action = partial(unit.turn, GO_UP)
                fct = self.game.getTopTile
        if fct is not None:
            return ContinuousPath(unit, self.game.getTileForUnit, fct, MAX_FPS, pre_action=pre_action,
                                  max_moves=-1 if not is_step else 1,
                                  step_post_action=partial(self._letTraceOnPreviousTile, unit=unit),
                                  units_location_dict=self.game.unitsLocation)
        raise UnfeasibleMoveException("The event couldn't create a valid move")

    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        """
        Encode a move to be performed (hence, this API must be in a state where the move represented by the descriptor
        has not yet been performed !)

        Args:
            player_number: The number representing the player that could perform the move
            move_descriptor: The descriptor of the move to be performed by the given player

        Returns:

            - -1 if the move makes it turn right, relatively to its current direction
            - 0 if the move makes it go straight, relatively to its current direction
            - +1 if the move makes it turn left, relatively to its current direction
            - -2 if the move makes it turn back (illegal move...)
        """
        diff = move_descriptor - self.game.getUnitForNumber(player_number).lastAction
        if abs(diff) == 2:
            return -2
        if diff == 3:
            return -1
        if diff == -3:
            return 1
        return diff

    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        """
        Decode the given encoded move to be performed by the given player into a move that can be directly
        understood by the game core.

        Args:
            player_number: The number representing the player that will perform the move
            encoded_move: The move that has been encoded into a relative move (between -1 and 1)

        Returns: The decoded move (absolute move, between 0 and 3)

        """
        if encoded_move == -2:
            return self.getCurrentDirection(player_number)
        new_move = self.getCurrentDirection(player_number) + encoded_move
        if new_move < 0:
            new_move += 4
        elif new_move > 3:
            new_move -= 4
        return new_move

    def getTileByteCode(self, tile_id: tuple) -> int:
        """
        Get the byte code of a tile

        Args:
            tile_id: The row and column-index of the tile (e.g. (x, y))

        Returns:
            The code representing the tile (i, j) in the board

                - 10 -> 13 indicates the current position of the player 1 + its current direction (0 to 3)
                - 20 -> 23 indicates the current position of the player 2 + its current direction (0 to 3)
                - 30 -> 33                    [...]                     3
                - 40 -> 43                    [...]                     4
                - -1 -> -4 indicates a tile occupied by a lazer put there by the player (no 1 to 4)
        """
        i, j = tile_id
        byte_code = 0
        occupants = self.game.getTileOccupants((i, j))
        if len(occupants) > 0:
            if len([occupants[i] for i in range(len(occupants)) if isinstance(occupants[i], Trace)]) > 0:  # Trace
                byte_code = -occupants[0].playerNumber
            elif occupants[0].isAlive():  # Player
                    byte_code = int(str(occupants[0].playerNumber) + str(occupants[0].currentAction))
        return byte_code

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
            for player_entity in player.getentitys():
                deadly_tiles.append(self.game.unitsLocation[player_entity])
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

    def getCurrentDirection(self, player_number: int):
        """

        Args:
            player_number: The number that represents the player for which it will return the current direction

        Returns: The current direction of the player (0: right, 1: top, 2: left, 3: bottom)
        """
        return self.game.getUnitForNumber(player_number).currentAction

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
        trace = Trace(unit.playerNumber, graphics=self.game.board.graphics is not None)
        if self.game.board.graphics is not None:
            self._resizeTrace(trace, self.game.board)
            trace.moveTo(tile_to_place_trace.center)
        self._previousTraces[unit] = trace
        self.game.addUnitToTile(tile_to_place_trace.identifier, trace)
        unit.addentity(trace)
