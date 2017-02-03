"""
File containing the definition of a Frame with buttons
"""

from tkinter import *
from tkinter.ttk import *
from typing import Tuple, Callable, List

from pytgf.menu.basicframe import BasicFrameBuilder


class ButtonFrameBuilder(BasicFrameBuilder):
    """
    Defines a Frame with a column of buttons
    """

    BUTTON_STYLE = "custom.TButton"

    def __init__(self, title: str, parent: Tk):
        """
        Instantiates a builder of a frame with a column of buttons

        Args:
            title: The title to give to the frame
            parent: The parent of the future frame
        """
        super().__init__(title, parent)
        self.buttons = []  # type: List[Tuple[str, Callable[[], None]]]

    def addButton(self, button_descriptor: Tuple[str, Callable[[], None]]):
        """
        Adds a button to the future frame

        Args:
            button_descriptor:
                The descriptor of the button to add to the frame. It's a tuple with the title of the button followed
                by the action to call when the button is clicked
        """
        self.buttons.append(button_descriptor)

    def addButtons(self, button_descriptors: List[Tuple[str, Callable[[], None]]]):
        """
        Adds buttons to the future frame

        Args:
            button_descriptors:
                A list containing the descriptors of the buttons to add to the frame, each button is a tuple with the
                title of the button followed by the action to call when the button is clicked
        """
        self.buttons.extend(button_descriptors)

    def create(self) -> Frame:
        """
        Creates the Frame

        Returns: The Frame with the button in its center
        """
        frame = super().create()
        self._addButtons(frame)
        return frame

    def _configureStyles(self) -> None:
        """
        The styles to configure for this Frame
        """
        super()._configureStyles()
        Style().configure(self.BUTTON_STYLE, width=15, padding=(0, 2, 0, 2), font="Helvetica 15")

    def _addButtons(self, frame: Frame) -> None:
        """
        Adds the real buttons inside the frame, using the button descriptors previously added to this builder

        Args:
            frame: The frame to which add the button
        """
        i = 1
        for button_string, action in self.buttons:
            bt = Button(frame, text=button_string, command=action, style=self.BUTTON_STYLE)
            bt.grid(row=i, column=1, pady=(0, 10))
            i += 1
        frame.grid_rowconfigure(index=i, pad=50, weight=1)
