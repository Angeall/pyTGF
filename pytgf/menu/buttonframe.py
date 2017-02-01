from tkinter import *
from tkinter.ttk import *

from pytgf.menu.basicframe import BasicFrameBuilder


class ButtonFrameBuilder(BasicFrameBuilder):

    BUTTON_STYLE = "custom.TButton"

    def __init__(self, title: str, parent: Tk):
        super().__init__(title, parent)
        self.buttons = []

    def addButton(self, button: tuple):
        self.buttons.append(button)

    def addButtons(self, buttons: list):
        self.buttons.extend(buttons)

    def create(self):
        frame = super().create()
        self._addButtons(frame)
        return frame

    def _configureStyles(self):
        super()._configureStyles()
        Style().configure(self.BUTTON_STYLE, width=15, padding=(0, 2, 0, 2), font="Helvetica 15")

    def _addButtons(self, frame):
        i = 1
        for button_string, action in self.buttons:
            bt = Button(frame, text=button_string, command=action, style=self.BUTTON_STYLE)
            bt.grid(row=i, column=1, pady=(0, 10))
            i += 1
        frame.grid_rowconfigure(index=i, pad=50, weight=1)


if __name__ == '__main__':
    parent = Tk()
    w = ButtonFrameBuilder("Test", parent)
    w.addButton(("Test1", lambda: 2))
    w.addButton(("Test2", lambda: 2))
    w.addButton(("Test3", lambda: 2))
    w.addButton(("Test4", lambda: 2))
    fr = w.create()
    fr.grid(row=0, column=0)
    parent.mainloop()


