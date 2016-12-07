import utils.geom
from characters.units.moving_unit import MovingUnit
from display.tile import Tile


class DeadlyMove(BaseException):  # The move is deadly
    pass


class IllegalMove(BaseException):  # The move is illegal but not deadly
    pass


class ImpossibleMove(BaseException):  # The move cannot be done because the wanted tile is not walkable
    pass


class ShortMove(object):
    """
    Represents a linear unit move between two tiles directly accessible.
    Can only make a straight movement.

    This class supposes that the unit comes from the center of the sourceTile.
    """
    def __init__(self, unit: MovingUnit, source_tile: Tile, destination_tile: Tile, fps: int):
        """
        Instantiates a move object between two tiles
        Args:
            unit: The unit to move
            source_tile: The tile from which the unit is moved
            destination_tile: The tile toward which the unit is moved
            fps: The number of _frames per second (refresh rate) used to determine the _frames needed to move the unit
        """
        self.isPerformed = False
        self.unit = unit
        self.sourceTile = source_tile
        self._currentPos = self.sourceTile.center
        self.destinationTile = destination_tile
        pixels_to_go_x = (destination_tile.center[0] - source_tile.center[0])
        pixels_to_go_y = (destination_tile.center[1] - source_tile.center[1])
        pixels_to_go = utils.geom.get_hypotenuse_length(pixels_to_go_x, pixels_to_go_y)
        seconds_needed = pixels_to_go / unit.speed
        self._frameNeeded = int(seconds_needed * fps)
        self._pixelsPerFrame = (pixels_to_go_x / self._frameNeeded, pixels_to_go_y / self._frameNeeded)

    def performStep(self):
        """
        Moves the unit toward the destination by a certain amount of pixels, computed
        Returns:

        """
        if self.destinationTile.deadly:
            raise DeadlyMove("The move that has been done is deadly and ends the game for this unit")
        if not self.destinationTile.walkable:
            raise ImpossibleMove("The destination is not walkable")
        if self.destinationTile.identifier not in self.sourceTile.neighbours:
            raise IllegalMove("The move from the source tile -- " + str(self.sourceTile.identifier) + " -- " +
                              "to the destination tile -- + " + str(self.destinationTile.identifier) + " -- " +
                              "cannot be performed")

        if not self.isPerformed:
            if self._frameNeeded <= 1:  # Last step => Complete the move (kill precision error)
                self.unit.moveTo(self.destinationTile.center)

                self.isPerformed = True
            else:
                temp_x = self._currentPos[0] + self._pixelsPerFrame[0]
                temp_y = self._currentPos[1] + self._pixelsPerFrame[1]
                self._currentPos = temp_x, temp_y
                self.unit.moveTo(self._currentPos)
                self._frameNeeded -= 1


