from pytgf.controls import HumanEvent


class KeyboardEvent(HumanEvent):
    def __init__(self, character_keys: tuple):
        """
        Instantiates a new keyboard event, which consists in the character keys that the user pressed

        Args:
            character_keys: The keys pressed by the user
        """
        self.characterKeys = character_keys  # type: tuple
