import pytgf.game as game
from pytgf.board import pathfinder, Board, Tile
from pytgf.board.pathfinder import UnreachableDestination
from pytgf.characters.moves import ListPath, ShortMove, Path
from pytgf.characters.units import MovingUnit
from pytgf.controls.events import KeyboardEvent
from pytgf.examples.sokoban.units.box import Box
from pytgf.game import Game
from pytgf.game.mainloop import MAX_FPS

FULL_HOLE_COLOR = (125, 125, 125)


class SokobanGame(Game):
    @property
    def _suicideAllowed(self) -> bool:
        return False

    @property
    def _teamKillAllowed(self) -> bool:
        return False

    def __init__(self, board: Board, ending_unit: MovingUnit, winning_tiles: list):
        super().__init__(board)
        self._endingUnit = ending_unit  # type: MovingUnit
        self._winningTiles = winning_tiles

    def createMoveForDescriptor(self, unit: MovingUnit, move_descriptor, max_moves: int=-1, force: bool=False) -> Path:
        if type(move_descriptor) == tuple and len(move_descriptor) == 2:
            destination_tile = self.board.getTileById(move_descriptor)
            if destination_tile.walkable:
                source_tile = self.board.getTileById(self.getTileForUnit(unit).identifier)
                moves = []
                try:
                    tile_ids = pathfinder.get_shortest_path(source_tile.identifier, destination_tile.identifier,
                                                            self.board.getTileById,
                                                            lambda tile: tile.neighbours,
                                                            lambda tile: tile.walkable and not tile.deadly)
                    current_tile = source_tile
                    tile_ids = self._checkIfBoxInTheWay(source_tile, tile_ids)
                    if max_moves > 0:
                        tile_ids = tile_ids[:max_moves]
                    if len(tile_ids) > 0:
                        for next_tile_id in tile_ids:
                            next_tile = self.board.getTileById(next_tile_id)
                            moves.append(ShortMove(unit, current_tile, next_tile, MAX_FPS,
                                                   units_location=self.unitsLocation))
                            current_tile = next_tile
                        return ListPath(moves, step_pre_action=self._pushBoxIfNeeded)
                except UnreachableDestination:
                    pass
        raise game.UnfeasibleMoveException()

    def _pushBoxIfNeeded(self, previous_tile: Tile, current_tile: Tile):
        box = None
        for occupant in self.getTileOccupants(current_tile.identifier):
            if isinstance(occupant, Box):
                box = occupant
                break
        if box is not None:
            prev_tile_id = previous_tile.identifier
            cur_tile_id = current_tile.identifier
            tile_diff = cur_tile_id[0] - prev_tile_id[0], cur_tile_id[1] - prev_tile_id[1]
            box_next_tile_id = (cur_tile_id[0] + tile_diff[0], cur_tile_id[1] + tile_diff[1])
            box_next_tile = self.board.getTileById(box_next_tile_id)
            if box_next_tile.deadly:  # The box falls into a hole
                self.board.setTileDeadly(box_next_tile_id, deadly=False)
                box.kill()
                if self.board.graphics is not None:
                    self.board.graphics.setInternalColor(FULL_HOLE_COLOR, box_next_tile_id[0], box_next_tile_id[1])
            event = box_next_tile_id
            self._addCustomMove(box, ListPath([ShortMove(box, current_tile, box_next_tile, MAX_FPS,
                                                         units_location=self.unitsLocation)]),
                                event)

    def _checkIfBoxInTheWay(self, source_tile: Tile, next_tile_ids: list) -> list:
        i = 0
        current = source_tile
        for tile_id in next_tile_ids:
            nxt = self.board.getTileById(tile_id)  # type: Tile
            for occupant in self.getTileOccupants(nxt.identifier):
                if isinstance(occupant, Box):
                    diff = (nxt.identifier[0] - current.identifier[0], nxt.identifier[1] - current.identifier[1])
                    box_next_tile_id = (nxt.identifier[0] + diff[0], nxt.identifier[1] + diff[1])
                    box_next_tile = self.board.getTileById(box_next_tile_id)  # The tile where the box will be
                    if not box_next_tile.walkable:
                        next_tile_ids = next_tile_ids[:i]
                        break
            current = nxt
            i += 1
        return next_tile_ids

    def _collidePlayers(self, player1, player2, frontal: bool = False):
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
            total_nb_players = len([u for u in self.players.values() if not isinstance(u, Box)
                                    and u is not self._endingUnit])
            self._endingUnit.setNbLives(total_nb_players - players_in_winning_tiles)  # if it is dead, the game ends

    def createKeyboardEvent(self, unit, input_key) -> KeyboardEvent:
        return SokobanKeyboardEvent(character_keys=(input_key,), player_tile_id=self.getTileIdForUnit(unit))


class SokobanKeyboardEvent(KeyboardEvent):
    def __init__(self, character_keys: tuple, player_tile_id: tuple):
        super().__init__(character_keys)
        self.playerTileID = player_tile_id

