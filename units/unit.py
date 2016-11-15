import pygame


class Unit(object):
    def __init__(self, sprite: pygame.sprite.Sprite):
        """

        Args:
            sprite:
            tile_id:
        """
        self.sprite = sprite  # type: pygame.sprite.Sprite
        self.group = None

    def drawAsSingleSprite(self, surface: pygame.Surface):
        if self.group is None:
            self.group = pygame.sprite.RenderPlain(self.sprite)
        self.group.draw(surface)
