from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_d, K_a, K_w, K_s, K_o, K_COMMA, K_k, K_l, K_g, K_t, K_f, K_h

from board.boards.square_board import SquareBoardBuilder
from board.tile import Tile
from characters.controllers.passive import PassiveController
from examples.sokoban.rules.game import SokobanGame
from examples.sokoban.tiles.winning import Winning
from examples.sokoban.units.box import Box
from examples.sokoban.units.sokobandrawstick import SokobanDrawstick
from game.mainloop import MainLoop

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]


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
        self._humanCounter = 0

    def createGame(self):
        board = super().create()
        i = 0
        winning_tiles = []
        for line in self._parserResult:
            j = 0
            for tile_type in line:  # Type: type
                tile = board.tiles[i][j]
                if tile_type == Box:
                    self._boxLocations.append((i, j))
                    tile_type = Tile
                elif tile_type == SokobanDrawstick:
                    self._playerLocations.append((i, j))
                    tile_type = Tile
                tile = tile_type(tile.graphics.center, tile.graphics.points, tile.identifier, neighbours=tile.neighbours)
                board.tiles[i][j] = tile
                if tile_type == Winning:
                    winning_tiles.append((i, j))
                j += 1
            i += 1
        game = SokobanGame(board, winning_tiles)
        main_loop = MainLoop(game)
        box_number = -1

        # PUT BOXES INTO THE GAME
        for (i, j) in self._boxLocations:
            main_loop.addUnit(Box(self._unitSpeed, box_number), PassiveController(box_number), (i, j), team=1)
            box_number -= 1

        # CHECK IF THERE IS ENOUGH PLAYERS SELECTED
        if len(self._controllers) < len(self._playerLocations):
            msg = "The number of players needed for this board is %d, got %d" % \
                    (len(self._controllers), len(self._playerLocations))
            raise NotEnoughPlayersException(msg)
        player_number = 1

        # PUT THE PLAYERS INTO THE GAME
        for (i, j) in self._playerLocations:
            controller = self._controllers[player_number - 1]
            try:
                controller = controller(player_number)
            except TypeError:  # Human player waiting for input keys
                keys = human_controls[self._humanCounter]
                self._humanCounter += 1
                controller = controller(player_number, keys[0], keys[1], keys[2], keys[3])
            main_loop.addUnit(SokobanDrawstick(self._unitSpeed, player_number), controller, (i, j), team=1)
            player_number += 1
        return main_loop


