"""
File containing the definition of a Mouse Event to send to Human Controllers
"""
from typing import Tuple

from .human import HumanEvent
from ...board import TileIdentifier

__author__ = 'Anthony Rouneau'


class MouseEvent(HumanEvent):
    """
    Defines an event representing a mouse click.
    """

    def __init__(self, pixel_clicked: tuple, mouse_state: Tuple[bool, bool, bool]=(True, False, False),
                 clicked_up: bool=False, tile_id: TileIdentifier=None):
        """
        Instantiates a new Mouse event, telling which pixel (and optionally which tile) has been clicked.

        Args:
            pixel_clicked: The pixel on which the user clicked
            mouse_state:
                The state of the mouse buttons. It is a triplet containing True at the i th position
                if the i th button of the mouse is pressed.
            clicked_up: True if the mouse event was a "up" event, False for a "down" event
            tile_id: The tile id that has been clicked (None if it is not a tile that was clicked)
        """
        self.pixelClicked = pixel_clicked
        self.mouseState = mouse_state
        self.clickedUp = clicked_up
        self.tileId = tile_id
