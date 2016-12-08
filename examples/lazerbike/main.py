from examples.lazerbike.controls.player import LazerBikePlayer
from display.boards.square_board import SquareBoardBuilder
import pygame
from pygame.locals import *

from examples.lazerbike.controls.allowed_moves import *
from examples.lazerbike.gameloop.game import LazerBikeGame
from examples.lazerbike.sprites.bike import Bike
from menu.aiselectorframe import AISelectorFrameBuilder
from menu.buttonframe import ButtonFrameBuilder
from menu.gui import GUI
from tkinter import Tk
from tkinter.ttk import Frame

human_controls = [(K_RIGHT, K_LEFT, K_UP, K_DOWN),
                  (K_d, K_a, K_w, K_s),
                  (K_COMMA, K_k, K_o, K_l),
                  (K_h, K_f, K_t, K_g)]

selection_frame = None
main_frame = None
nb_human = 0


def get_selection_frame() -> Frame:
    global selection_frame
    return selection_frame


def buildMainFrame(window: Tk, gui: GUI) -> Frame:
    global selection_frame, main_frame
    builder = ButtonFrameBuilder("LazerBike", window)
    builder.setTitleColor("#FF0000")
    builder.addButton(("Play", lambda: gui.goToFrame(get_selection_frame())))
    builder.addButton(("Quit", gui.quit))
    main_frame = builder.create()
    return main_frame


def buildSelectionFrame(window: Tk, gui: GUI) -> Frame:
    global selection_frame
    builder = AISelectorFrameBuilder("Player selection", window, LazerBikePlayer,
                                     lambda: launch_game(gui, builder.getSelection()), gui.goToPreviousFrame,
                                     max_teams=4, min_teams=2,
                                     players_description={1: "Blue", 2: "Red", 3: "Green", 4: "Yellow"})
    selection_frame = builder.create()
    return selection_frame


def get_player_info(player_number: int):
    if player_number == 1:
        return 17, 25, GO_RIGHT
    elif player_number == 2:
        return 37, 50, GO_LEFT
    elif player_number == 3:
        return 4, 37, GO_DOWN
    else:
        return 45, 37, GO_UP


def add_player(game: LazerBikeGame, player_class, player_number: int, player_team: int, speed: int):
    global nb_human
    print(player_class)
    try:
        controller = player_class(player_number)
    except TypeError:
        controls = human_controls[nb_human]
        nb_human += 1
        controller = player_class(player_number, controls[0], controls[1], controls[2], controls[3])
    player_info = get_player_info(player_number)
    start_pos = player_info[0:2]
    initial_direction = player_info[2]
    game.addUnit(Bike(speed, player_number, max_trace=-1), controller, start_pos, initial_direction, team=player_team)


def launch_game(gui: GUI, player_info: tuple):
    gui.quit()
    pygame.init()
    width = 1280
    height = 500
    builder = SquareBoardBuilder(width, height, 50, 75)
    builder.setBordersColor((0, 125, 125))
    builder.setBackgroundColor((25, 25, 25))
    builder.setTilesVisible(False)
    board = builder.create()
    speed = int(round((min(width, height) / 1080) * 150))
    game = LazerBikeGame(board)
    player_classes = player_info[0]
    player_teams = player_info[1]
    for player_number, player_class in player_classes.items():
        add_player(game, player_class, player_number, player_teams[player_number], speed)

    result = game.run()
    if len(result) == 0:
        print("DRAW")
    else:
        winning_players_strings = ["Player " + str(number) for number in result]
        print("WON: ", winning_players_strings)


def launch_gui():
    window = Tk()
    gui = GUI("Lazerbike", window)
    gui.addFrame(buildMainFrame(window, gui))
    gui.addFrame(buildSelectionFrame(window, gui))
    gui.mainloop()


if __name__ == "__main__":
    launch_gui()
