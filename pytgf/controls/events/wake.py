from .bot import BotEvent


class WakeEvent(BotEvent):
    def __init__(self):
        super().__init__(-1, None)
