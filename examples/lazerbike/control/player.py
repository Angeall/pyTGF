from abc import ABCMeta

from controls.controller import Controller
from examples.lazerbike.control.linker import GO_RIGHT, GO_UP, GO_LEFT, GO_DOWN


class LazerBikePlayer(Controller, metaclass=ABCMeta):
    def __init__(self, player_number):
        super().__init__(player_number)

    def goLeft(self):
        self.moves.put(GO_LEFT)

    def goRight(self):
        self.moves.put(GO_RIGHT)

    def goUp(self):
        self.moves.put(GO_UP)

    def goDown(self):
        self.moves.put(GO_DOWN)
