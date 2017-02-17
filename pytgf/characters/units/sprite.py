"""
File containing the abstract definition of a sprite designed to be linked with a unit
"""

import os
from abc import ABCMeta, abstractmethod
from copy import deepcopy

import pygame
import pygame.transform as transform

__author__ = 'Anthony Rouneau'


class UnitSprite(pygame.sprite.Sprite, metaclass=ABCMeta):
    """
    Abstract definition of a unit's sprite.
    """

    def __init__(self):
        """
        Instantiates the sprite
        """
        super().__init__()
        self.resFolder = os.path.join("res", "sprites")
        location = os.path.join(os.curdir, self.imageRelativePath)
        img = pygame.image.load_extended(location)  # type: pygame.Surface
        # img = img.convert_alpha()
        self.image = img
        self.rect = img.get_rect()  # type: pygame.Rect

    def rotate(self, angle: float) -> None:
        """
        Rotates this sprite

        Args:
            angle: The angle in degrees
        """
        if self.image is not None and self.rect is not None:
            self.image = transform.rotate(self.image, angle)
            self.rect = self.image.get_rect()  # type: pygame.Rect

    def size(self, width: int, height: int) -> None:
        """
        Resize this sprite.

        Args:
            width: The new width
            height: The new height
        """
        if self.image is not None and self.rect is not None:
            self.image = transform.scale(self.image, (width, height))
            (x, y) = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.move_ip(x, y)

    @property
    @abstractmethod
    def imageRelativePath(self) -> str:
        """
        Contains the relative path to the image of this sprite.
        """
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


