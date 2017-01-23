from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_d, K_a, K_w, K_s, K_o, K_COMMA, K_k, K_l, K_g, K_t, K_f, K_h

from gameboard.boards.square_board import SquareBoardBuilder
from gameboard.tile import Tile
from characters.units.moving_unit import MovingUnit
from controls.controllers.bot import Bot
from controls.controllers.human import Human
from controls.controllers.passive import PassiveController
from examples.sokoban.controllers.linker import SokobanBotLinker, SokobanHumanLinker
from examples.sokoban.rules.sokoban import SokobanGame
from examples.sokoban.tiles.winning import Winning
from examples.sokoban.units.box import Box
from examples.sokoban.units.sokobandrawstick import SokobanDrawstick
from game.mainloop import MainLoop

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]


class NeverEndingGame(Exception):
    pass


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
        self._game = None
        self._mainLoop = None

    def createGame(self):
        board = super().create()
        winning_tiles = self._addTiles(board)
        ending_unit = self._createEndingUnit(winning_tiles)
        self._game = SokobanGame(board, ending_unit, winning_tiles)
        self._game.addUnit(ending_unit, team_number=1000, origin_tile_id=(-1, -1))
        self._mainLoop = MainLoop(self._game)
        self._addBoxes()
        self._addPlayers()
        return self._mainLoop

    def _addTiles(self, board):
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
                tile = tile_type(tile.graphics.center, tile.graphics.points, tile.identifier,
                                 neighbours=tile.neighbours)
                board.tiles[i][j] = tile
                if tile_type == Winning:
                    winning_tiles.append(tile)
                j += 1
            i += 1
        return winning_tiles

    def _addPlayers(self):
        # CHECK IF THERE IS ENOUGH PLAYERS SELECTED
        if len(self._controllers) < len(self._playerLocations):
            msg = "The number of players needed for this board is %d, got %d" % \
                  (len(self._controllers), len(self._playerLocations))
            raise NotEnoughPlayersException(msg)
        player_number = 1
        # PUT THE PLAYERS INTO THE GAME
        for (i, j) in self._playerLocations:
            controller = self._controllers[player_number - 1]
            if issubclass(controller, Bot):
                linker = SokobanBotLinker(controller(player_number))
            elif issubclass(controller, Human):  # Human player waiting for input keys
                keys = human_controls[self._humanCounter]
                self._humanCounter += 1
                linker = SokobanHumanLinker(controller(player_number, keys[0], keys[1], keys[2], keys[3]))
            else:
                raise TypeError("The type of the player (\'%s\') must either be a Bot or a Human subclass."
                                % (str(controller)))
            self._mainLoop.addUnit(SokobanDrawstick(self._unitSpeed, player_number), linker, (i, j), team=1)
            player_number += 1

    def _addBoxes(self):
        box_number = -1
        for (i, j) in self._boxLocations:
            self._mainLoop.addUnit(Box(self._unitSpeed, box_number),
                                   SokobanBotLinker(PassiveController(box_number)), (i, j), team=2)
            box_number -= 1

    def _createEndingUnit(self, winning_tiles):
        ending_unit = MovingUnit(1000)
        if len(winning_tiles) == 0:
            raise NeverEndingGame("No winning tiles were given to the game, resulting in a never ending game.")
        for tile in winning_tiles:
            tile.addOccupant(ending_unit)
        return ending_unit


