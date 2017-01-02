import loop.game as game
from board import pathfinder
from board.board import Board
from board.pathfinder import UnreachableDestination
from board.tile import Tile
from characters.controller import Controller
from characters.controllers.human import Human
from characters.moves.listpath import ListPath
from characters.moves.move import ImpossibleMove, ShortMove
from characters.units.unit import Unit
from examples.sokoban.units.box import Box
from loop.game import Game


class NeverEndingGame(Exception):
    pass


class SokobanGame(Game):
    def updateGameState(self, unit, tile_id):
        players_units = [unit for unit in self._units if not isinstance(unit, Box)]

        super().updateGameState(unit, tile_id)


    def __init__(self, board: Board, winning_tiles: list):
        super().__init__(board)
        if len(winning_tiles) == 0:
            raise NeverEndingGame("No winning tiles were given to the game, resulting in a never ending game.")
        self._winningTiles = winning_tiles
        self._endingUnit = Unit()
        self.addUnit(self._endingUnit, None)
        self.addToTeam(1000, self._endingUnit)

    def _sendInputToHumanController(self, controller: Human, input_key: int) -> None:
        controller.reactToInput(input_key, player_tile=self._units[self.controllers[controller]])

    def _isFinished(self) -> (bool, list):
        units = []
        for controller in self.controllers:
            winning = False
            unit = self.controllers[controller]
            if not isinstance(unit, Box):
                units.append(unit)
                for winning_tile in self._winningTiles:
                    if self._units[unit] == winning_tile:
                        winning = True
                        break
                if not winning:
                    return False, []
        return True, units

    def _sendMouseEventToHumanController(self, controller: Human, tile: Tile, mouse_state: tuple,
                                         click_up: bool) -> None:
        if tile is not None:
            controller.reactToTileClicked(tile.identifier, mouse_state, click_up,
                                          player_tile=self._units[self.controllers[controller]])

    def _handleControllerEvent(self, controller: Controller, event) -> None:
        if type(event) == tuple and len(event) == 2:
            if self._controllersMoves[controller][0] is None:
                destination_tile = self.board.getTileById(event)
                if destination_tile.walkable:
                    unit = self._getUnitFromController(controller)
                    source_tile = self.board.getTileById(self._units[unit])
                    moves = []
                    try:
                        tile_ids = pathfinder.get_shortest_path(source_tile.identifier, destination_tile.identifier,
                                                                self.board.getTileById, lambda tile: tile.neighbours,
                                                                lambda tile: tile.walkable and not tile.deadly)
                        current_tile = source_tile
                        tile_ids = self._checkIfBoxInTheWay(source_tile, tile_ids)
                        if len(tile_ids) > 0:
                            for next_tile_id in tile_ids:
                                next_tile = self.board.getTileById(next_tile_id)
                                moves.append(ShortMove(unit, current_tile, next_tile, game.MAX_FPS))
                                current_tile = next_tile
                            self._addMove(controller, ListPath(moves, step_pre_action=self._pushBoxIfNeeded))
                    except UnreachableDestination:
                        pass

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
            self._addOtherMove(box, ListPath([ShortMove(box, current_tile, box_next_tile, game.MAX_FPS)]))

    def _checkIfBoxInTheWay(self, source_tile: Tile, next_tile_ids: list) -> list:
        i = 0
        current = source_tile
        for tile_id in next_tile_ids:
            nxt = self.board.getTileById(tile_id)
            for occupant in nxt.occupants:
                if isinstance(occupant, Box):
                    diff = (nxt.identifier[0] - current.identifier[0], nxt.identifier[1] - current.identifier[1])
                    box_next_tile_id = (nxt.identifier[0] + diff[0], nxt.identifier[1] + diff[1])
                    box_next_tile = self.board.getTileById(box_next_tile_id)  # The tile where the box will be pushed
                    if not box_next_tile.walkable:
                        next_tile_ids = next_tile_ids[:i]
                        break
            current = nxt
            i += 1
        return next_tile_ids
