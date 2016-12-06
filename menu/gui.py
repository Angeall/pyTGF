from tkinter import *
from menu.buttonframe import ButtonFrameBuilder
from utils.gui import center_window


class GUI:
    def __init__(self, title: str, parent: Tk):
        self._parent = parent
        parent.title(title)
        parent.minsize(1024, 576)
        center_window(parent)
        parent.grid_rowconfigure(index=0, weight=1)
        parent.grid_columnconfigure(index=0, weight=1)
        self._frames = []
        self._currentFrame = None
        self._previousFrame = None

    def addFrame(self, frame: Frame) -> None:
        self._frames.append(frame)
        if len(self._frames) == 1:
            self._currentFrame = frame
            self.goToFrameAtIndex(0)

    def goToFrameAtIndex(self, index: int) -> None:
        self.goToFrame(self._frames[index])

    def goToFrame(self, next_frame: Frame) -> None:
        if self._currentFrame is not None:
            self._currentFrame.grid_remove()  # Removes the current Frame from the GUI
        self._previousFrame = self._currentFrame
        self._currentFrame = next_frame
        self._currentFrame.grid(row=0, column=0, sticky='news')  # Adds the new current frame to the GUI

    def goToPreviousFrame(self) -> None:
        self.goToFrame(self._previousFrame)

    def quit(self):
        self._parent.destroy()

    def mainloop(self):
        self._parent.mainloop()