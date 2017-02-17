from abc import ABCMeta

from pytgf.controls.wrappers import ControllerWrapper, HumanControllerWrapper, BotControllerWrapper


class SokobanControllerWrapper(ControllerWrapper, metaclass=ABCMeta):
    def isMoveDescriptorAllowed(self, move_descriptor) -> bool:
        return True


class SokobanHumanControllerWrapper(HumanControllerWrapper, SokobanControllerWrapper):
    pass


class SokobanBotControllerWrapper(BotControllerWrapper, SokobanControllerWrapper):
    pass
