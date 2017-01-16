import game.game as game
from board import pathfinder
from board.board import Board
from board.pathfinder import UnreachableDestination
from board.tile import Tile
from characters.moves.listpath import ListPath
from characters.moves.move import ShortMove
from characters.moves.path import Path
from characters.units.moving_unit import MovingUnit
from controls.events.keyboard import KeyboardEvent
from examples.sokoban.units.box import Box
from game.game import Game
from game.mainloop import MAX_FPS


class NeverEndingGame(Exception):
    pass


class SokobanGame(Game):
    def __init__(self, board: Board, winning_tiles: list):
        if winning_tiles is None or len(winning_tiles) == 0:
            raise NeverEndingGame("No winning tiles were given to the game, resulting in a never ending game.")
        super().__init__(board)
        self._winningTiles = winning_tiles
        self._endingUnit = MovingUnit(1000)
        self.addUnit(self._endingUnit, 1000, (-1, -1))

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
                            moves.append(ShortMove(unit, current_tile, next_tile, MAX_FPS))
                            current_tile = next_tile
                        return ListPath(moves, step_pre_action=self._pushBoxIfNeeded)
                except UnreachableDestination:
                    pass
        raise game.UnfeasibleMoveException()

    def updateGameState(self, unit, tile_id):
        if tile_id in self._winningTiles:
            players_units = [u for u in self.units if not isinstance(u, Box) and u is not self._endingUnit]
            nb_player = len(players_units) - 1
            for u in players_units:
                if self.units[u] in self._winningTiles:
                    nb_player -= 1
            self._endingUnit.setNbLives(nb_player)
        super().updateGameState(unit, tile_id)
        if self.isFinished():
            self.winningPlayers = [player for player in self.winningPlayers
                                   if not isinstance(player, Box) and player is not self._endingUnit]

    def _pushBoxIfNeeded(self, previous_tile: Tile, current_tile: Tile):
        box = None
        for occupant in current_tile.occupants:
            if isinstance(occupant, Box):
                box = occupant
                break
        if box is not None:
            prev_tile_id = previous_tile.identifier
            cur_tile_id = current_tile.identifier
            tile_diff = cur_tile_id[0] - prev_tile_id[0], cur_tile_id[1] - prev_tile_id[1]
            box_next_tile_id = (cur_tile_id[0] + tile_diff[0], cur_tile_id[1] + tile_diff[1])
            box_next_tile = self.board.getTileById(box_next_tile_id)
            self._addCustomMove(box, ListPath([ShortMove(box, current_tile, box_next_tile, MAX_FPS)]))

    def _checkIfBoxInTheWay(self, source_tile: Tile, next_tile_ids: list) -> list:
        i = 0
        current = source_tile
        for tile_id in next_tile_ids:
            nxt = self.board.getTileById(tile_id)
            for occupant in nxt.occupants:
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

    def createKeyboardEvent(self, unit, input_key) -> KeyboardEvent:
        return SokobanKeyboardEvent(character_keys=(input_key,), player_tile_id=self.units[unit])


class SokobanKeyboardEvent(KeyboardEvent):
    def __init__(self, character_keys: tuple, player_tile_id: tuple):
        super().__init__(character_keys)
        self.playerTileID = player_tile_id

