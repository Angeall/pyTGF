"""
File containing the definition of a Builder for a Basic Frame
"""

from tkinter import *
from tkinter.ttk import *

from typing import Tuple, Union

TkColor = Union[Tuple, str]


class BasicFrameBuilder:
    """
    Defines a basic container Frame
    """

    TITLE_STYLE = "title.TLabel"
    FRAME_STYLE = "main.TFrame"

    def __init__(self, title: str, parent: Tk):
        """
        Instantiates a new Frame

        Args:
            title: The title of the frame
            parent: The parent of the frame
        """
        self.backgroundColor = "#FFFFFF"
        self.titleColor = "#000000"
        self.buttons = []
        self.title = title
        self.parent = parent

    def setBackgroundColor(self, background_color: TkColor) -> None:
        """
        Sets the background color of the frame

        Args:
            background_color: The color to set to the background of the frame
        """
        self.backgroundColor = background_color

    def setTitleColor(self, title_color: TkColor) -> None:
        """
        Sets the tile color of the frame

        Args:
            title_color: The color to set to the title of the frame
        """
        self.titleColor = title_color

    def create(self) -> Frame:
        """
        Creates the Frame
        """
        self._configureStyles()
        frame = Frame(self.parent, style=self.FRAME_STYLE)
        self._configureWeight(frame)
        self._addTitle(frame)
        return frame

    def _configureStyles(self) -> None:
        """
        Creates the styles needed for this frame
        """
        Style().configure(self.TITLE_STYLE, foreground=self.titleColor, background=self.backgroundColor,
                          padding=(0, 50, 0, 175), font="Helvetica 30 bold")
        Style().configure(self.FRAME_STYLE, background=self.backgroundColor)

    def _configureWeight(self, frame: Frame) -> None:
        """
        Configure the columns of this frame

        Args:
            frame: The frame to configure
        """
        frame.grid_columnconfigure(index=0, weight=2)
        frame.grid_columnconfigure(index=1, weight=3)  # Column that contains the buttons
        frame.grid_columnconfigure(index=2, weight=2)

    def _addTitle(self, frame: Frame) -> None:
        """
        Adds the tile to the frame

        Args:
            frame: The frame to which wa will add the title
        """
        title = Label(frame, text=self.title, style="title.TLabel")
        title.grid(row=0, column=1)


