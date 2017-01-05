from queue import Queue

from characters.controller import Controller


class SokobanPlayer(Controller):
    def __init__(self, player_number):
        super().__init__(player_number)
        self.moves = Queue()

    def goToTile(self, tile_id):
        """
        Asks the rules to go to the tile for which the ID has been given
        Args:
            tile_id: The IF of the tile to which the player must go
        """
        self.moves.put(tile_id)
