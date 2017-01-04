import utils.geom
from characters.units.moving_unit import MovingUnit
from board.tile import Tile


class IllegalMove(BaseException):  # The move is illegal
    pass


class ImpossibleMove(BaseException):  # The move cannot be done because the wanted tile is not walkable by the unit
    pass


class InconsistentMove(ImpossibleMove):  # The move use a source tile that does not contain the given unit.
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
        self._totalFrameNeeded = self._frameNeeded
        self._pixelsPerFrame = (pixels_to_go_x / self._frameNeeded, pixels_to_go_y / self._frameNeeded)

    def isConsistent(self):
        return self.unit in self.sourceTile

    def performStep(self, backward=False):
        """
        Moves the unit toward the destination by a certain amount of pixels, computed following a MAX_FPS value and
        the distance between the two tiles

        Args:
            backward: If True, makes the step coming from the destination to the source. Default: False
        """
        if not self.destinationTile.walkable:
            self.cancelMove()
            raise ImpossibleMove("The destination is not walkable")
        if self.destinationTile.identifier not in self.sourceTile.neighbours:
            self.cancelMove()
            raise IllegalMove("The move from the source tile -- " + str(self.sourceTile.identifier) + " -- " +
                              "to the destination tile -- + " + str(self.destinationTile.identifier) + " -- " +
                              "cannot be performed")
        if not self.isConsistent():
            self.cancelMove()
            raise InconsistentMove("The tile %s does not contain the given unit" % self.sourceTile.identifier)

        if not self.isPerformed:
            if self._frameNeeded <= 1:  # Last step => Complete the move (kill precision error)
                self.unit.moveTo(self.destinationTile.center)
                self._handleLastStep()
                self.isPerformed = True
            else:
                if backward:
                    temp_x = self._currentPos[0] - self._pixelsPerFrame[0]
                    temp_y = self._currentPos[1] - self._pixelsPerFrame[1]
                    self._frameNeeded += 1
                else:
                    temp_x = self._currentPos[0] + self._pixelsPerFrame[0]
                    temp_y = self._currentPos[1] + self._pixelsPerFrame[1]
                    self._frameNeeded -= 1
                self._currentPos = temp_x, temp_y
                self.unit.moveTo(self._currentPos)

    def completeMove(self):
        for _ in range(self._frameNeeded):
            self.performStep()

    def _handleLastStep(self):
        if self.unit in self.sourceTile:
            self.sourceTile.removeOccupant(self.unit)
            self.destinationTile.addOccupant(self.unit)

    def cancelMove(self):
        frames_already_done = self._totalFrameNeeded - self._frameNeeded
        for _ in range(frames_already_done):
            self.unit.moveTo(self.sourceTile.center)
        self.isPerformed = True


