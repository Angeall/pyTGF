from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_d, K_a, K_w, K_s, K_o, K_COMMA, K_k, K_l, K_g, K_t, K_f, K_h

from ..controllers.wrapper import SokobanBotControllerWrapper, SokobanHumanControllerWrapper
from ..parsing.parser import TileProperty, box, winning, player_tile
from ..rules.sokoban import SokobanGame
from ..rules.sokobanapi import SokobanAPI
from ..units.box import Box
from ..units.sokobandrawstick import SokobanDrawstick
from ....board import Board, Builder
from ....characters.units import Unit
from ....controls.controllers.bot import Bot
from ....controls.controllers.human import Human
from ....game.realtime import RealTimeMainLoop

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]


class NeverEndingGame(Exception):
    pass


class NotEnoughPlayersException(Exception):
    pass


class SokobanBoardBuilder(Builder):
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
        for tile in winning_tiles:
            self._game.addUnit(ending_unit, team_number=1000, origin_tile_id=tile.identifier, controlled=False,
                               active=True)
        self._mainLoop = RealTimeMainLoop(SokobanAPI(self._game))
        self._addBoxes()
        self._addPlayers()
        return self._mainLoop

    def _addTiles(self, board: Board):
        i = 0
        winning_tiles = []
        for line in self._parserResult:
            j = 0
            for tile_property in line:  # type: TileProperty
                tile = board.getTileById((i, j))
                if tile_property == box:
                    self._boxLocations.append((i, j))
                elif tile_property == player_tile:
                    self._playerLocations.append((i, j))
                if tile_property.border_color is not None:
                    board.graphics.setBorderColor(tile_property.border_color, i, j)
                if tile_property.internal_color is not None:
                    board.graphics.setInternalColor(tile_property.internal_color, i, j)
                board.setTileDeadly((i, j), deadly=tile_property.deadly)
                board.setTileNonWalkable((i, j), walkable=tile_property.walkable)
                if tile_property == winning:
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
                linker = SokobanBotControllerWrapper(controller(player_number))
            elif issubclass(controller, Human):  # Human player waiting for input keys
                keys = human_controls[self._humanCounter]
                self._humanCounter += 1
                linker = SokobanHumanControllerWrapper(controller(player_number, keys[0], keys[1], keys[2], keys[3]))
            else:
                raise TypeError("The type of the player (\'%s\') must either be a Bot or a Human subclass."
                                % (str(controller)))
            self._mainLoop.addUnit(SokobanDrawstick(self._unitSpeed, player_number), linker, (i, j), team=1)
            player_number += 1

    def _addBoxes(self):
        box_number = -1
        for (i, j) in self._boxLocations:
            self._mainLoop.addUnit(Box(self._unitSpeed, box_number),
                                   None, (i, j), team=2)
            box_number -= 1

    @staticmethod
    def _createEndingUnit(winning_tiles):
        ending_unit = Unit(1000)
        if len(winning_tiles) == 0:
            raise NeverEndingGame("No winning tiles were given to the game, resulting in a never ending game.")
        return ending_unit


