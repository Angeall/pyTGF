from abc import ABCMeta, abstractmethod

from pytgf.game import API


class AbstractRoutine(metaclass=ABCMeta):

    @abstractmethod
    def routine(self, player_number: int, state: API):
        pass