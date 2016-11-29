import pygame
from pygame import gfxdraw

import utils.geom
from characters.particle import Particle


class NotAPolygonError(BaseException):
    pass


class OccupantNotFoundError(BaseException):
    pass


class Tile(object):
    """
    Represent a tile on the game board, which is represented by an equilateral polygon
    """

    TILE_LENGTH_EPSILON = 0.1

    def __init__(self, center: tuple, points: list, identifier, walkable: bool=True, deadly: bool=False) -> None:
        """
        Args:
            center: The equidistant center of the tile
            points: The points that will be used to draw the polygon (not closed), it will be closed by connecting
                    the last and the first point
            identifier: The identifier of the tile in the board
            walkable: Boolean that defines if a unit can walk on this tile or not
            deadly: Boolean that defines if a unit must die when walking on this tile
        """
        self.nbrOfSides = len(points)
        if self.nbrOfSides < 3:
            raise NotAPolygonError("A polygon is made of minimum 3 points")
        self.identifier = identifier
        self.neighbours = []
        self.center = center
        self.points = points
        self.sideLength = int(utils.geom.dist(self.points[-1], self.points[0]))
        assert self._isEquilateral()
        self._convexHull = None    # Is initialized when needed, at the call of self.containsPoint
        self._hullPath = None      # Is initialized when needed, at the call of self.containsPoint
        self.deadly = deadly
        self.walkable = walkable
        self.externalColor = (0, 0, 0)
        self.internalColor = None
        self._occupants = []

    @property
    def occupants(self):
        to_remove = []
        for occupant in self._occupants:  # type: Particle
            if not occupant.isAlive():
                to_remove.append(occupant)
        self.removeOccupant(to_remove)
        return self._occupants

    @occupants.setter
    def occupants(self, value):
        self._occupants = value

    def setExternalColor(self, external_color: tuple) -> None:
        """
        Sets the color of the tile's borders (default: black)
        Args:
            external_color: RGB (or RGBA) tuple that defines the color of the tile's sides
        """
        self.externalColor = external_color

    def setInternalColor(self, internal_color: tuple) -> None:
        """
        Set the color of the tile's body (default: transparent)
        Args:
            internal_color: RGB (or RGBA) tuple that defines the tile's internal color
        """
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

    def containsPoint(self, point: tuple) -> bool:
        """
        Checks if a point lies inside the tile
        Args:
            point: The point to check

        Returns: True if the point is inside and False otherwise
        """
        if self._convexHull is None:
            self._convexHull = utils.geom.get_convex_hull(self.points)
        assert self._convexHull is not None
        if self._hullPath is None:
            self._hullPath = utils.geom.get_path(self.points, self._convexHull)
        assert self._hullPath is not None
        return self._hullPath.contains_point(point)

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the tile and its occupants on the given surface
        Args:
            surface: The surface on which the tile will be drawn
        """
        if self.internalColor is not None:
            gfxdraw.filled_polygon(surface, self.points, self.internalColor)
        gfxdraw.aapolygon(surface, self.points, self.externalColor)
        # pygame.draw.aaline(surface, self.externalColor, self.points[-1], self.points[0])

        for occupant in self.occupants:  # type: Particle
            occupant.draw(surface)

    def addOccupant(self, new_occupant) -> None:
        """
        Adds an occupant to this tile
        Args:
            new_occupant: The occupant to add to this tile
        """
        self.occupants.append(new_occupant)

    def __contains__(self, item):
        # TODO: Checks if the tile contains a unit and if the unit is alive ! if not, remove it from the tile
        pass

    def removeOccupant(self, occupant_to_remove) -> None:
        """
        Removes an occupant from this tile
        Args:
            occupant_to_remove: The occupant to remove from this tile

        Raises:
            OccupantNotFoundError: If the given occupant is not present in the tile.
        """
        if isinstance(occupant_to_remove, Particle):
            if occupant_to_remove in self._occupants:
                self._occupants.remove(occupant_to_remove)
            else:
                raise OccupantNotFoundError(
                    "The occupant " + str(occupant_to_remove) + " was not found in the tile " + str(self.identifier))
        elif isinstance(occupant_to_remove, list):
            new_occupants = []
            for occupant in self._occupants:  # type: Particle
                if new_occupants not in occupant_to_remove:
                    new_occupants.append(occupant)
            self.occupants = new_occupants

    def clearOccupants(self) -> None:
        """
        Removes all the occupants from this tile
        """
        self.occupants = []

    def _isEquilateral(self):
        """
        Checks if the polygon is equilateral
        Returns: True if all the length are equal with a epsilon-accuracy.
        """
        length = utils.geom.dist(self.points[0], self.points[1])
        i = 1
        while i < len(self.points) - 1:
            computed_length = utils.geom.dist(self.points[i], self.points[i+1])
            if abs(computed_length - length) > self.TILE_LENGTH_EPSILON:
                return False
            i += 1
        return abs(utils.geom.dist(self.points[len(self.points)-1], self.points[0]) - length) < self.TILE_LENGTH_EPSILON

    def hasTwoOrMoreOccupants(self):
        """
        Returns: True if this tile has two or more occupants
        """
        return len(self._occupants) >= 2
