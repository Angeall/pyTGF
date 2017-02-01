from collections import namedtuple
from typing import Union, Dict, Tuple, List

import numpy as np
import pygame
from scipy.spatial import KDTree

from pytgf.board.graphics import BoardGraphics
from pytgf.utils.geom import Coordinates

Tile = namedtuple("Tile", "identifier center deadly walkable neighbours")
TileIdentifier = Tuple[int, int]


class Board:
    OUT_OF_BOARD_TILE = Tile(identifier=(-1, -1), center=(-500, -500), deadly=True, walkable=True, neighbours=())

    def __init__(self, lines: int, columns: int, tiles: Dict[TileIdentifier, Tile],
                 centers: List[List[Coordinates]], borders: List[Tuple[Coordinates, Coordinates]],
                 tiles_borders: List[List[List[Coordinates]]]):
        """
        Instantiates a game board using the given parameters

        Args:
            lines: The number of lines in the board
            columns: The number of columns in the board
            tiles:
                A dict containing all the Tile structs, representing the tiles in the board,
                accessible through their identifier (i, j), i being the row index and j being the column index.
            centers: The list containing the matrix of centers for the tiles. Used to associate a pixel to a tile.
            borders:
                A list of lines, represented by two points each, representing the borders of the board.
                 (e.g. [((1, 2), (3, 4)), ((0,1), (0,2)), ...])
            tiles_borders: The points that will serve to draw the tiles
        """
        self.graphics = BoardGraphics(tiles_borders=tiles_borders, background_color=(255, 255, 255),
                                      border_line_color=(0, 0, 0), borders=borders, tiles_visible=False)
        self.lines = lines
        self.columns = columns
        self._tiles = tiles  # type: Dict[tuple, Tile]
        self._kdTree = KDTree(np.array(centers).reshape(1, len(centers) * len(centers[0]), 2)[0])

    def getTileByPixel(self, pixel: Coordinates) -> Union[Tile, None]:
        """
        Get the tile located on the given pixel

        Args:
            pixel: The _screen coordinates on which we want to get the tile

        Returns: The tile located on the pixel, or None if there is no tile at this position

        """
        if self.graphics is not None:
            center_index = self._kdTree.query(pixel, 1)[1]
            i = center_index // self.columns
            j = center_index - (self.columns * i)
            if self.graphics.containsPoint(pixel, i, j):
                return self._tiles[(i, j)]
        return None

    def getTileById(self, identifier: TileIdentifier) -> Tile:
        """

        Args:
            identifier: A tuple containing the row and the column index of the wanted tile

        Returns: The Tile struct located at the given identifier
        """
        try:
            return self._tiles[identifier]
        except KeyError:
            return self.OUT_OF_BOARD_TILE

    def isAccessible(self, source_identifier: TileIdentifier, destination_identifier: TileIdentifier) -> bool:
        """

        Args:
            source_identifier:
                The identifier (i, j) that identifies the tile from which we want to access the destination tile
            destination_identifier:
                The identifier (i, j) that identifies the tile that we want to access from the source tile.

        Returns: True if the identifier is in the neighbourhood of the given source tile.
        """
        tile = self._tiles[source_identifier]
        return (tile.neighbours is not None and self.getTileById(destination_identifier).walkable) and (
               destination_identifier in tile.neighbours)

    def getNeighboursIdentifier(self, tile_identifier: TileIdentifier) -> Tuple[TileIdentifier]:
        """

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours

        Returns: A tuple containing the identifiers of the neighbours of the tile for which the identifier was given.
        """
        return self._tiles[tile_identifier].neighbours

    def setTileDeadly(self, tile_identifier: TileIdentifier, deadly: bool=True) -> None:
        """
        Modifies the "deadly" property of a tile

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours
            deadly: If True, the tile will be set as "deadly", else, set the tile as "non-deadly"
        """
        tile = self._tiles[tile_identifier]
        self._tiles[tile_identifier] = Tile(identifier=tile.identifier, center=tile.center, neighbours=tile.neighbours,
                                            deadly=deadly, walkable=tile.walkable)

    def setTileNonWalkable(self, tile_identifier: TileIdentifier, walkable: bool=False) -> None:
        """
        Modifies the "deadly" property of a tile

        Args:
            tile_identifier: The identifier of the tile from which we want the neighbours
            walkable: If False, the tile will be set as "non-walkable", else, sets the the tile as "walkable"
        """
        tile = self._tiles[tile_identifier]
        self._tiles[tile_identifier] = Tile(identifier=tile.identifier, center=tile.center, neighbours=tile.neighbours,
                                            deadly=tile.deadly, walkable=walkable)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the board on the given surface

        Args:
            surface: The surface on which draw the board
        """
        if self.graphics is not None:
            self.graphics.draw(surface)

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k == "_tiles":
                value = {a: b for a, b in v.items()}
            elif k == "_kdTree" or k == "graphics":
                value = None
            else:
                value = v
            setattr(result, k, value)
        return result
