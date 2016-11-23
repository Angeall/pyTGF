from abc import ABCMeta, abstractmethod
import asyncio

from characters.controller import Controller
from characters.unit import Unit
from display.tile import Tile


class Human(Controller, metaclass=ABCMeta):

    @abstractmethod
    def reactToInput(self, input_key: int, *game_info: ...) -> None:
        """
        Makes the controller react to an input. (e.g. input_key == K_RIGHT: self.moves.put(Move(right=True)) )
        Args:
            input_key: The key of the keyboard input to react to. See pygame.locals "K_...".
            game_info: All the useful game information used, for example, for path-finding purpose.
        """
        pass

    @abstractmethod
    def reactToTileClicked(self, tile, mouse_state=(True, False, False), click_up=False, *game_info: ...) -> None:
        """

        Args:
            tile: The tile clicked on (can be None if click_up = True)
            mouse_state: A triplet containing the mouse state (can be 3*False): (b1_clicked, b2_clicked, b3_clicked)
                         Default: left click down
            click_up: True if the event is a "mouseup" event. False otherwise
            game_info: All the useful game information used, for example, for path-finding purpose.
        """
        pass
