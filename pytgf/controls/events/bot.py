"""
File containing the definition of a BotEvent used to be sent to BotControllers
"""
from .event import Event
from ...characters.moves import MoveDescriptor

__author__ = 'Anthony Rouneau'


class BotEvent(Event):
    """
    Represents a move done inside the main game that is to be replicated inside the bot's local copy of the game.
    """

    def __init__(self, player_number: int, move_descriptor: MoveDescriptor):
        """
        Constructs the event to pass to the bot controller

        Args:
            player_number: The number of the player that performed the given move
            move_descriptor:
                The description of the move performed by the given player (depends on the game). Should give an
                actual Path object when giving it to the game's ""
        """
        self.playerNumber = player_number
        self.moveDescriptor = move_descriptor
