from pygame import gfxdraw
import pygame


class NotAPolygonError(BaseException):
    pass


class Tile(object):
    def __init__(self, center: tuple, points: list, identifier: tuple,
                 external_color: tuple = (0, 0, 0), internal_color: tuple = None) -> None:
        """
        Args:
            center: The equidistant center of the tile
            points: The points that will be used to draw the polygon (not closed), it will be closed by connecting
                    the last and the first point
            identifier: The identifier of the tile in the board
            external_color: RGB (or RGBA) tuple that defines the color of the tile's sides
            internal_color: RGB (or RGBA) tuple that defines the tile's internal color
        """
        self.nbrOfSides = len(points)
        if self.nbrOfSides < 3:
            raise NotAPolygonError("A polygon is made of a minimum of 3 points")
        self.identifier = identifier
        self.neighbours = []
        self.center = center
        self.points = points
        self.walkable = False
        self.externalColor = external_color
        self.internalColor = internal_color

    def addNeighbour(self, neighbour_identifier: tuple) -> None:
        """
        Adds a neighbours, accessible from this tile
        Args:
            neighbour_identifier: The identifier of the new neighbour of the tile
        """
        self.neighbours.append(neighbour_identifier)

    def addNeighbours(self, neighbours_identifier: list) -> None:
        """
        Add multiple neighbours, accessible from this tile
        Args:
            neighbours_identifier: A list of identifiers of the new accessible tiles to add as neighbours to this tile
        """
        self.neighbours.extend(neighbours_identifier)

    def hasDirectAccess(self, other_tile_identifier) -> bool:
        """
        Checks if the tile has a direct access to another tile.
        Args:
            other_tile_identifier: Identifier of the other tile
        Returns: True if the other tile is in the direct neighbourhood of this tile.
        """
        return other_tile_identifier in self.neighbours

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the tile on the given surface
        Args:
            surface: The surface on which the tile will be drawn
        """
        if self.internalColor is not None:
            gfxdraw.filled_polygon(surface, self.points, self.internalColor)
        gfxdraw.aapolygon(surface, self.points, self.externalColor)
        pygame.draw.aaline(surface, self.externalColor, self.points[-1], self.points[0])
