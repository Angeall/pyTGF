from abc import ABCMeta, abstractmethod

from characters.controller import Controller


class Human(Controller, metaclass=ABCMeta):

    @abstractmethod
    def reactToInput(self, input_key: int, **game_info: ...) -> None:
        """
        Makes the controller react to an input. (e.g. input_key == K_RIGHT: self.moves.put(Move(right=True)) )
        Args:
            input_key: The key of the keyboard input to react to. See pygame.locals "K_...".
            game_info: All the useful game information used, for example, for path-finding purpose.
        """
        pass

    @abstractmethod
    def reactToTileClicked(self, tile_id, mouse_state=(True, False, False), click_up=False, **game_info: ...) -> None:
        """

        Args:
            tile_id: The ID of the tile clicked on (can be None if the click was outside any tile)
            mouse_state: A triplet containing the mouse state (can be 3*False): (b1_clicked, b2_clicked, b3_clicked)
                         Default: left click down
            click_up: True if the event is a "mouseup" event. False otherwise
            game_info: All the useful game information used, for example, for path-finding purpose.
        """
        pass
