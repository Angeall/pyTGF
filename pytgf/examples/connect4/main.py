from tkinter import Tk
from tkinter.ttk import Frame, Label, Button

import pygame

from pytgf.examples.connect4.builder import create_game
from pytgf.examples.connect4.controllers import Connect4Player
from pytgf.menu import AISelectorFrameBuilder, ButtonFrameBuilder, GUI

selection_frame = None  # type: Frame
main_frame = None


def get_selection_frame() -> Frame:
    return selection_frame


def buildMainFrame(window: Tk, gui: GUI) -> Frame:
    global main_frame
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
    main_loop = create_game(player_info[0], 768, 768, True)
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
