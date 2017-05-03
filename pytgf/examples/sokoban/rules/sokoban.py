from typing import Optional

from ....board import Board, TileIdentifier
from ....characters.units import Entity, Unit
from ....controls.events import KeyboardEvent
from ....game import Core

FULL_HOLE_COLOR = (125, 125, 125)


class SokobanGame(Core):
    @property
    def _suicideAllowed(self) -> bool:
        return False

    @property
    def _teamKillAllowed(self) -> bool:
        return False

    def __init__(self, board: Board, ending_unit: Unit, winning_tiles: list):
        super().__init__(board)
        self._endingUnit = ending_unit  # type: Unit
        self._winningTiles = winning_tiles

    def _collidePlayers(self, player1: Unit, player2: Unit, tile_id: TileIdentifier, frontal: bool = False,
                        entity: Optional[Entity]=None):
        """
        Checks if the player1 is colliding with the invisible player

        Args:
            player1: The first given player
            player2: The second given player
            frontal: If true, the collision is frontal and kills the two players
        """
        if player1 is self._endingUnit or player2 is self._endingUnit:
            self._handleEndingUnitCollision(player1, player2)

    def _handleEndingUnitCollision(self, player1, player2):
        other_unit = None
        if player1 is self._endingUnit:
            other_unit = player2
        elif player2 is self._endingUnit:
            other_unit = player1
        if other_unit is not None:
            players_in_winning_tiles = 0
            for tile in self._winningTiles:
                players_in_winning_tiles += \
                    len(self.getTileOccupants(tile.identifier)) - 1  # -1 because the end unit is in each winning tile
            total_nb_players = len(self.avatars)
            self._endingUnit.setNbLives(total_nb_players - players_in_winning_tiles)  # if it is dead, the game ends

    def createKeyboardEvent(self, unit, input_key) -> KeyboardEvent:
        return SokobanKeyboardEvent(character_keys=(input_key,), player_tile_id=self.getTileIdForUnit(unit))


class SokobanKeyboardEvent(KeyboardEvent):
    def __init__(self, character_keys: tuple, player_tile_id: tuple):
        super().__init__(character_keys)
        self.playerTileID = player_tile_id

