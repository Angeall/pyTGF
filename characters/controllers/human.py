from characters.controller import Controller
from abc import ABCMeta, abstractmethod


class Human(Controller, metaclass=ABCMeta):

    @abstractmethod
    def reactToInput(self, input_key=None, game_state=None) -> None:
        """
        Makes the controller react to an input. (e.g. input_key == K_RIGHT: self.moves.put(Move(right=True)) )
        Args:
            input_key: The key of the keyboard input to react to (can be None). See pygame.locals "K_...".
            mouse_state:
            game_state: All the useful game information (can be None) used, for example, for path-finding purpose.
        """
        pass

    @abstractmethod
    def reactToTileClicked(self, tile, mouse_state=(False, False, False), click_up=False) -> None:
        """

        Args:
            tile: The tile clicked on (can be None if click_up = True)
            mouse_state: A triplet containing the mouse state (can be 3*False): (b1_clicked, b2_clicked, b3_clicked)
            click_up: True if the event is a "mouseup" event. False otherwise
        """
        pass
