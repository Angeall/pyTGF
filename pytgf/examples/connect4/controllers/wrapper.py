from abc import ABCMeta

from pytgf.controls.wrappers import ControllerWrapper, HumanControllerWrapper, BotControllerWrapper


__author__ = "Anthony Rouneau"


class Connect4ControllerWrapper(ControllerWrapper, metaclass=ABCMeta):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return type(move_descriptor) == int


class Connect4HumanControllerWrapper(HumanControllerWrapper, Connect4ControllerWrapper):
    pass


class Connect4BotControllerWrapper(BotControllerWrapper, Connect4ControllerWrapper):
    pass
