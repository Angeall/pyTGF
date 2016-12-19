from board.boards.square_board import SquareBoardBuilder
from board.tile import Tile
from characters.controllers.passive import PassiveController
from examples.sokoban.gameloop.game import SokobanGame
from examples.sokoban.units.box import Box
from examples.sokoban.units.player import Player


class NotEnoughPlayersException(Exception):
    pass


class SokobanBoardBuilder(SquareBoardBuilder):
    def __init__(self, width: int, height: int, parser_result: list, controllers: list, unit_speed: int):
        super().__init__(width, height, len(parser_result), len(parser_result[0]))
        self._boxLocations = []
        self._playerLocations = []
        self._parserResult = parser_result
        self._controllers = controllers
        self._unitSpeed = unit_speed

    def createGame(self):
        board = super().create()
        i = 0
        for line in self._parserResult:
            j = 0
            for tile_type in line:  # Type: type
                tile = board.tiles[i][j]
                if tile_type == Box:
                    self._boxLocations.append((i, j))
                    tile_type = Tile
                elif tile_type == Player:
                    self._playerLocations.append((i, j))
                    tile_type = Tile
                board.tiles[i][j] = tile_type(tile.center, tile.points, tile.identifier)
                j += 1
            i += 1
        game = SokobanGame(board)
        box_identifier = -1
        for (i, j) in self._boxLocations:
            game.addUnit(Box(self._unitSpeed, box_identifier), PassiveController(box_identifier), (i, j), team=2)
            box_identifier -= 1

        if len(self._controllers) < len(self._playerLocations):
            msg = "The number of players needed for this board is %d, got %d" % \
                    (len(self._controllers), len(self._playerLocations))
            raise NotEnoughPlayersException(msg)
        player_number = 1

        for (i, j) in self._playerLocations:
            game.addUnit(Player(self._unitSpeed, player_number), self._controllers[player_number-1], (i, j))
            player_number += 1


