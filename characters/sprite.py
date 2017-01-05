import os

import pygame
import pygame.transform as transform
from abc import ABCMeta, abstractmethod

from copy import deepcopy


class UnitSprite(pygame.sprite.Sprite, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        location = os.path.join(os.curdir, self.imageName)
        img = pygame.image.load_extended(location)  # type: pygame.Surface
        # img = img.convert_alpha()
        self.image = img
        self.rect = img.get_rect()  # type: pygame.Rect

    def rotate(self, angle: float):
        self.image = transform.rotate(self.image, angle)
        self.rect = self.image.get_rect()  # type: pygame.Rect

    def size(self, width: int, height: int):
        self.image = transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect()

    @property
    @abstractmethod
    def imageName(self):
        pass

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "image" and k != "rect":
                value = deepcopy(v, memo)
            else:
                value = None
            setattr(result, k, value)
        return result


