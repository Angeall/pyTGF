"""
File containing the definition of the API used by the bot controllers of the Lazerbike game
"""
from typing import List

from pytgf.board import TileIdentifier
from pytgf.game import GameState

GO_RIGHT = 0
GO_UP = 1
GO_LEFT = 2
GO_DOWN = 3


class LazerBikeGameState(GameState):
    """
    Defines the API with which the controllers can communicate
    """

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
