from typing import List

from pytgf.board import Builder
from pytgf.controls.controllers import Bot
from pytgf.controls.controllers import Human
from pytgf.examples.connect4.controllers import Connect4BotControllerWrapper
from pytgf.examples.connect4.controllers import Connect4HumanControllerWrapper
from pytgf.examples.connect4.rules import Connect4API
from pytgf.examples.connect4.rules import Connect4Core
from pytgf.examples.connect4.units import Bottom
from pytgf.examples.connect4.units import Connect4Unit
from pytgf.game.mainloop import MainLoop

__author__ = "Anthony Rouneau"


def add_controller(main_loop: MainLoop, player_classes: List):
    assert len(player_classes) == 2
    for i, player_class in enumerate(player_classes):
        player_number = i + 1
        if issubclass(player_class, Bot):
            linker = Connect4BotControllerWrapper(player_class(player_number))
        elif issubclass(player_class, Human):
            linker = Connect4HumanControllerWrapper(player_class(player_number))
        else:
            raise TypeError("The type of the player (\'%s\') must either be a Bot or a Human subclass."
                            % (str(player_class)))
        main_loop.addUnit(Connect4Unit(player_number), linker, main_loop.game.board.OUT_OF_BOARD_TILE.identifier,
                          team=player_number)


def create_game(selected_classes: dict, width: int, height: int, graphics: bool=True) -> MainLoop:
    lines = 6
    columns = 7
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 0, 0))
    builder.setTilesVisible(True)
    board = builder.create()
    board.graphics = board.graphics if graphics else None

    game = Connect4Core(board)
    main_loop = MainLoop(Connect4API(game), turn_by_turn=True)
    player_classes = [None, None]
    for player_number, player_class in selected_classes.items():
        player_classes[player_number - 1] = player_class
    add_controller(main_loop, player_classes)
    for i in range(7):
        game.addUnit(Bottom(1000 + i), game.BOTTOM_TEAM_NUMBER, (5, i))
    return main_loop
