import pygame.image
import os


class BikeSprite(pygame.sprite.Sprite):
    def __init__(self) -> None:
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self)
        location = os.path.join(os.curdir, "bike.png")
        img = pygame.image.load_basic(location)  # type: pygame.Surface
        img = img.convert_alpha()
        self.image = img
        self.rect = img.rect()  # type: pygame.Rect

    def moveTo(self, x:int, y: int) -> None:
        x_offset = x - self.rect.x
        y_offset = y - self.rect.y
        self.rect.move_ip(x_offset, y_offset)

