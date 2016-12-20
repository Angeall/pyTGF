from queue import Queue

from characters.controller import Controller


class SokobanPlayer(Controller):
    def __init__(self, player_number):
        super().__init__(player_number)
        self.moves = Queue()
