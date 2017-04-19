from pygame.locals import *

from pytgf.board import Builder
from pytgf.controls.controllers import Bot, Human
from pytgf.examples.lazerbike.control import LazerBikeBotControllerWrapper, LazerBikeHumanControllerWrapper
from pytgf.examples.lazerbike.gamedata import GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN
from pytgf.examples.lazerbike.rules import LazerBikeCore, LazerBikeAPI
from pytgf.examples.lazerbike.units.bike import Bike
from pytgf.game.realtime import RealTimeMainLoop

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]

nb_human = 0


def get_player_info(player_number: int):
    if player_number == 1:
        return 2, 2, GO_RIGHT
    elif player_number == 2:
        return 12, 12, GO_LEFT
    elif player_number == 3:
        return 12, 2, GO_UP
    else:
        return 2, 12, GO_DOWN


def add_controller(main_loop: RealTimeMainLoop, player_class, player_number: int, player_team: int, speed: int,
                   max_trace: int):
    global nb_human
    if issubclass(player_class, Bot):
        linker = LazerBikeBotControllerWrapper(player_class(player_number))
    elif issubclass(player_class, Human):
        controls = human_controls[nb_human % len(human_controls)]
        nb_human += 1
        linker = LazerBikeHumanControllerWrapper(player_class(player_number, controls[0], controls[1], controls[2],
                                                              controls[3]))
    else:
        raise TypeError("The type of the player (\'%s\') must either be a Bot or a Human subclass."
                        % (str(player_class)))
    player_info = get_player_info(player_number)
    start_pos = player_info[0:2]
    initial_direction = player_info[2]
    main_loop.addUnit(Bike(speed, player_number, max_trace=max_trace, initial_direction=initial_direction),
                      linker, start_pos, initial_direction, team=player_team)


def create_game(player_info: tuple):
    global nb_human
    width = 1024
    height = 768
    lines = 15
    columns = 15
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    # builder.setTilesVisible(True)
    board = builder.create()
    # board.graphics.setBorderColor((0, 125, 125))
    # board.graphics.setInternalColor((25, 25, 25))

    speed = 0.75 * board.graphics.sideLength
    game = LazerBikeCore(board)
    main_loop = RealTimeMainLoop(LazerBikeAPI(game))
    player_classes = player_info[0]
    player_teams = player_info[1]
    for player_number, player_class in player_classes.items():
        add_controller(main_loop, player_class, player_number, player_teams[player_number], int(speed),
                       int(min(lines, columns) * (2 / 3)))
    nb_human = 0
    return main_loop
