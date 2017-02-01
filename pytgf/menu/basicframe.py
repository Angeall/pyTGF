from tkinter import *
from tkinter.ttk import *


class BasicFrameBuilder:

    TITLE_STYLE = "title.TLabel"
    FRAME_STYLE = "main.TFrame"

    def __init__(self, title: str, parent: Tk):
        self.backgroundColor = "#FFFFFF"
        self.titleColor = "#000000"
        self.buttons = []
        self.title = title
        self.parent = parent

    def setBackgroundColor(self, background_color):
        self.backgroundColor = background_color

    def setTitleColor(self, title_color):
        self.titleColor = title_color

    def create(self):
        self._configureStyles()
        frame = Frame(self.parent, style=self.FRAME_STYLE)
        self._configureWeight(frame)
        self._addTitle(frame)
        return frame

    def _configureStyles(self):
        Style().configure(self.TITLE_STYLE, foreground=self.titleColor, background=self.backgroundColor,
                          padding=(0, 50, 0, 175), font="Helvetica 30 bold")
        Style().configure(self.FRAME_STYLE, background=self.backgroundColor)

    def _configureWeight(self, frame):
        frame.grid_columnconfigure(index=0, weight=2)
        frame.grid_columnconfigure(index=1, weight=3)  # Column that contains the buttons
        frame.grid_columnconfigure(index=2, weight=2)

    def _addTitle(self, frame: Frame):
        title = Label(frame, text=self.title, style="title.TLabel")
        title.grid(row=0, column=1)


if __name__ == '__main__':
    parent = Tk()
    w = BasicFrameBuilder("Test", parent)
    frame = w.create()
    frame.grid(row=0, column=0)
    parent.mainloop()


