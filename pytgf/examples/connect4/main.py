from tkinter import Tk
from tkinter.ttk import Frame, Label, Button
from typing import List

import pygame

from pytgf.board import Builder
from pytgf.controls.controllers import Bot, Human
from pytgf.examples.connect4.controllers import Connect4BotControllerWrapper, Connect4HumanControllerWrapper, Connect4Player
from pytgf.examples.connect4.rules import Connect4Core, Connect4API
from pytgf.examples.connect4.units import Bottom, Connect4Unit
from pytgf.game.mainloop import MainLoop
from pytgf.menu import AISelectorFrameBuilder, ButtonFrameBuilder, GUI

selection_frame = None
main_frame = None


def get_selection_frame() -> Frame:
    global selection_frame
    return selection_frame


def buildMainFrame(window: Tk, gui: GUI) -> Frame:
    global selection_frame, main_frame
    builder = ButtonFrameBuilder("Connect4", window)
    builder.setTitleColor("#FF0000")
    builder.addButton(("Play", lambda: gui.goToFrame(get_selection_frame())))
    builder.addButton(("Quit", gui.quit))
    main_frame = builder.create()
    return main_frame


def buildSelectionFrame(window: Tk, gui: GUI) -> Frame:
    global selection_frame
    builder = AISelectorFrameBuilder("Player selection", window, Connect4Player,
                                     lambda: launch_game(gui, builder.getSelection()), gui.goToPreviousFrame,
                                     min_players=2, max_players=2,
                                     max_teams=1, min_teams=1,
                                     players_description={1: "First Player", 2: "Second Player"})
    selection_frame = builder.create()
    return selection_frame


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


def end_popup(string_result):
    popup = Tk()
    popup.title('Game finished')
    label = Label(popup, text=string_result)
    label.grid(row=0, column=0, columnspan=4)
    button1 = Button(text="Play again", command=lambda: relaunch_gui(popup), width=15)
    button1.grid(row=1, column=1)
    button2 = Button(text="Quit", command=popup.destroy, width=15)
    button2.grid(row=1, column=2)


def launch_game(gui: GUI, player_info: tuple):
    gui.quit()
    pygame.init()
    width = 768
    height = 768
    lines = 6
    columns = 7
    builder = Builder(width, height, lines, columns)
    builder.setBordersColor((0, 0, 0))
    builder.setTilesVisible(True)
    board = builder.create()

    game = Connect4Core(board)
    main_loop = MainLoop(Connect4API(game), turn_by_turn=True)
    player_classes = [None, None]
    for player_number, player_class in player_info[0].items():
        player_classes[player_number-1] = player_class
    add_controller(main_loop, player_classes)
    for i in range(7):
        game.addUnit(Bottom(1000 + i), game.BOTTOM_TEAM_NUMBER, (5, i))

    result = main_loop.run()
    if result is None:
        return
    elif len(result) == 0:
        string_result = "DRAW"
    else:
        winning_players_strings = ["Player " + str(player.playerNumber) for player in result]
        string_result = "WON: " + str(winning_players_strings)
    end_popup(string_result)


def relaunch_gui(window):
    pygame.quit()
    window.destroy()
    launch_gui()


def launch_gui():
    window = Tk()
    gui = GUI("Connect 4", window)
    gui.addFrame(buildMainFrame(window, gui))
    gui.addFrame(buildSelectionFrame(window, gui))
    gui.mainloop()


if __name__ == "__main__":
    launch_gui()
