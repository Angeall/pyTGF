from characters.controller import Controller
from examples.lazerbike.controls.allowed_moves import *


class LazerBikePlayer(Controller):
    def __init__(self, player_number):
        super().__init__()
        self.playerNumber = player_number

    def goLeft(self):
        self.moves.put(GO_LEFT)

    def goRight(self):
        self.moves.put(GO_RIGHT)

    def goUp(self):
        self.moves.put(GO_UP)

    def goDown(self):
        self.moves.put(GO_DOWN)
