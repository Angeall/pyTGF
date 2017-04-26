from typing import Tuple, Dict, Type, Optional

from pygame.locals import *

from .control import LazerBikeBotControllerWrapper, LazerBikeHumanControllerWrapper
from .gamedata import GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN, Direction
from .rules import LazerBikeCore, LazerBikeAPI
from .units.bike import Bike
from ...board import Builder
from ...controls.controllers import Bot, Human
from ...game.realtime import RealTimeMainLoop

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]

nb_human = 0


default_initial_positions = {1: (2, 2, GO_RIGHT), 2: (12, 12, GO_LEFT), 3: (12, 2, GO_UP), 4: (2, 12, GO_DOWN)}


def add_controller(main_loop: RealTimeMainLoop, player_class, player_number: int, player_team: int, speed: int,
                   max_trace: int, init_positions, graphics):
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
    player_info = init_positions[player_number]
    start_pos = player_info[0:2]
    initial_direction = player_info[2]
    main_loop.addUnit(Bike(speed, player_number, max_trace=max_trace, initial_direction=initial_direction,
                           graphics=graphics),
                      linker, start_pos, initial_direction, team=player_team)


def create_game(player_info: Tuple[Dict[int, Type], Dict[int, int]], width: int=1024, height: int=768, lines: int=15,
                columns: int=15, init_positions: Dict[int, Tuple[int, int, Direction]]=default_initial_positions,
                speed: Optional[int]=None, max_trace: int=-1, graphics: bool=True):
    global nb_human
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()

    if speed is None:
        speed = 0.33 * board.graphics.sideLength
    game = LazerBikeCore(board)
    main_loop = RealTimeMainLoop(LazerBikeAPI(game))
    player_classes = player_info[0]
    player_teams = player_info[1]
    for player_number, player_class in player_classes.items():
        add_controller(main_loop, player_class, player_number, player_teams[player_number], int(speed),
                       max_trace, init_positions, graphics)
    nb_human = 0
    return main_loop
