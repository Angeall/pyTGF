"""
File containing the definition of a GUI, a container of Frames
"""

from tkinter import *

from ..utils.gui import center_window


class GUI:
    """
    Defines a GUI containing multiple Frames.
    """
    def __init__(self, title: str, parent: Tk):
        """
        Instantiates a GUI

        Args:
            title: The title of this GUI
            parent: The parent of the GUI
        """
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
        """
        Add a new Frame to this GUI

        Args:
            frame: The new frame to add to the GUI
        """
        self._frames.append(frame)
        if len(self._frames) == 1:
            self._currentFrame = frame
            self.goToFrameAtIndex(0)

    def goToFrameAtIndex(self, index: int) -> None:
        """
        Makes the wanted frame visible

        Args:
            index: The number representing the frame that we want to be visible
        """
        self.goToFrame(self._frames[index])

    def goToFrame(self, next_frame: Frame) -> None:
        """
        Make the given frame visible in the GUI

        Args:
            next_frame: The frame to make visible
        """
        if self._currentFrame is not None:
            self._currentFrame.grid_remove()  # Removes the current Frame from the GUI
        self._previousFrame = self._currentFrame
        self._currentFrame = next_frame
        self._currentFrame.grid(row=0, column=0, sticky='news')  # Adds the new current frame to the GUI

    def goToPreviousFrame(self) -> None:
        """
        Make the previous Frame visible
        """
        self.goToFrame(self._previousFrame)

    def quit(self) -> None:
        """
        Destroys the GUI
        """
        self._parent.destroy()

    def mainloop(self) -> None:
        """
        Make the GUI visible
        """
        self._parent.mainloop()
