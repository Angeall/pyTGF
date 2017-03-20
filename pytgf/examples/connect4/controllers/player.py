from abc import ABCMeta

from pytgf.controls.controllers import Controller


__author__ = "Anthony Rouneau"


class Connect4Player(Controller, metaclass=ABCMeta):
    pass