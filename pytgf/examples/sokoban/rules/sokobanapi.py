from ..rules.sokoban import FULL_HOLE_COLOR
from ..units.box import Box
from ....board import Tile, pathfinder
from ....characters.moves import ListPath, MoveDescriptor, Path, ShortMove
from ....characters.units import Unit
from ....controls.wrappers.wrapper import MAX_FPS
from ....game import UnfeasibleMoveException
from ....game.realtime import API


class SokobanAPI(API):
    def createMoveForDescriptor(self, unit: Unit, move_descriptor, force: bool=False, is_step: bool=False) \
            -> Path:
        if isinstance(move_descriptor, tuple) and len(move_descriptor) == 2:
            destination_tile = self.game.board.getTileById(move_descriptor)
            if destination_tile.walkable:
                source_tile = self.game.board.getTileById(self.game.getTileForUnit(unit).identifier)
                moves = []
                try:
                    tile_ids = pathfinder.get_shortest_path(source_tile.identifier, destination_tile.identifier,
                                                            self.game.board.getTileById,
                                                            lambda tile: tile.neighbours,
                                                            lambda tile: tile.walkable and not tile.deadly)
                    current_tile = source_tile
                    tile_ids = self._checkIfBoxInTheWay(source_tile, tile_ids)
                    if len(tile_ids) > 0:
                        for next_tile_id in tile_ids:
                            next_tile = self.game.board.getTileById(next_tile_id)
                            moves.append(ShortMove(unit, current_tile, next_tile, MAX_FPS,
                                                   units_location=self.game.unitsLocation))
                            current_tile = next_tile
                        return ListPath(unit, moves, step_pre_action=self._pushBoxIfNeeded)
                except pathfinder.UnreachableDestination:
                    pass
        raise UnfeasibleMoveException()

    def _encodeMoveIntoPositiveNumber(self, player_number: int, move_descriptor: MoveDescriptor) -> int:
        return move_descriptor[0] + (move_descriptor[1] << 16)

    def _decodeMoveFromPositiveNumber(self, player_number: int, encoded_move: int) -> MoveDescriptor:
        y = encoded_move >> 16
        x = encoded_move - (y << 16)
        return x, y

    def _pushBoxIfNeeded(self, previous_tile: Tile, current_tile: Tile):
        box = None
        for occupant in self.game.getTileOccupants(current_tile.identifier):
            if isinstance(occupant, Box):
                box = occupant
                break
        if box is not None:
            prev_tile_id = previous_tile.identifier
            cur_tile_id = current_tile.identifier
            tile_diff = cur_tile_id[0] - prev_tile_id[0], cur_tile_id[1] - prev_tile_id[1]
            box_next_tile_id = (cur_tile_id[0] + tile_diff[0], cur_tile_id[1] + tile_diff[1])
            box_next_tile = self.game.board.getTileById(box_next_tile_id)
            if box_next_tile.deadly:  # The box falls into a hole
                self.game.board.setTileDeadly(box_next_tile_id, deadly=False)
                box.kill()
                if self.game.board.graphics is not None:
                    self.game.board.graphics.setInternalColor(FULL_HOLE_COLOR, box_next_tile_id[0], box_next_tile_id[1])
            event = box_next_tile_id
            self.game.addCustomMove(box, ListPath(box, [ShortMove(box, current_tile, box_next_tile, MAX_FPS / 2,
                                                  units_location=self.game.unitsLocation)]),
                                    event)

    def _checkIfBoxInTheWay(self, source_tile: Tile, next_tile_ids: list) -> list:
        i = 0
        current = source_tile
        for tile_id in next_tile_ids:
            nxt = self.game.board.getTileById(tile_id)  # type: Tile
            for occupant in self.game.getTileOccupants(nxt.identifier):
                if isinstance(occupant, Box):
                    diff = (nxt.identifier[0] - current.identifier[0], nxt.identifier[1] - current.identifier[1])
                    box_next_tile_id = (nxt.identifier[0] + diff[0], nxt.identifier[1] + diff[1])
                    box_next_tile = self.game.board.getTileById(box_next_tile_id)  # The tile where the box will be
                    if not box_next_tile.walkable:
                        next_tile_ids = next_tile_ids[:i]
                        break
            current = nxt
            i += 1
        return next_tile_ids
