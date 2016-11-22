import os

import pygame
from abc import ABCMeta, abstractmethod


class UnitSprite(pygame.sprite.Sprite, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        location = os.path.join(os.curdir, self.imageName)
        img = pygame.image.load_extended(location)  # type: pygame.Surface
        # img = img.convert_alpha()
        self.image = img
        self.rect = img.get_rect()  # type: pygame.Rect

    @property
    @abstractmethod
    def imageName(self):
        pass


