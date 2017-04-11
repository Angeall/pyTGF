"""
File containing the rules of the Lazerbike game
"""
from typing import Optional

from pytgf.board import Tile
from pytgf.board import TileIdentifier
from pytgf.characters.units import MovingUnit
from pytgf.characters.units import Particle
from pytgf.examples.lazerbike.gamedata import GO_UP, GO_DOWN, GO_LEFT, GO_RIGHT
from pytgf.game.core import Core


class LazerBikeCore(Core):
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

    def _collidePlayers(self, player1: MovingUnit, player2: MovingUnit, tile_id: TileIdentifier, frontal: bool=False,
                        particle: Optional[Particle]=None) -> None:
        """
        Makes what it has to be done when the first given player collides with a particle of the second given player
        (Careful : two moving units (alive units) colliding each other causes a frontal collision that hurts both
        units)

        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
        """
        return super()._collidePlayers(player1, player2, tile_id, frontal=frontal, particle=particle)

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
