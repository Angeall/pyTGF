import pygame
from queue import Queue, Empty

import utils.geom
from characters.sprite import UnitSprite


class Unit(object):
    # TODO: Make an abstraction between an alive unit, a unit with a sprite, etc...
    def __init__(self, sprite: UnitSprite, speed: float = 150, max_particles: int=-1):
        """
        Instantiates a character unit in the game
        Args:
            sprite: The sprite to draw on the board
            speed: The speed, in pixels per seconds, of the unit when moving
            max_particles: The maximum number of particles for this unit (-1 = infinite)
        """
        self.sprite = sprite  # type: UnitSprite
        self._drawable = None
        self._particles = pygame.sprite.Group()
        self._particlesQueue = Queue()
        self.speed = speed
        self.currentAction = None

    def isAlive(self):
        return self.sprite.isAlive()

    def draw(self, surface: pygame.Surface) -> None:
        if self._drawable is None:
            self._drawable = pygame.sprite.RenderPlain(self.sprite)
        self._particles.draw(surface)
        self._drawable.draw(surface)

    def addParticle(self, sprite: UnitSprite) -> None:
        self._particlesQueue.put(sprite)
        self._particles.add(sprite)

    def removeOldestParticle(self) -> None:
        try:
            oldest_sprite = self._particlesQueue.get_nowait()
            self._particles.remove(oldest_sprite)
        except Empty:
            pass

    def removeParticle(self, sprite: UnitSprite) -> None:
        temp_queue = Queue()
        try:
            while True:  # Will stop when the Empty exception comes out from the Queue
                current = self._particlesQueue.get_nowait()
                if current is not sprite:
                    temp_queue.put(current)
        except Empty:
            pass
        finally:
            self._particlesQueue = temp_queue
            self._particles.remove(sprite)

    def moveTo(self, destination: tuple) -> None:
        """
        Move the center of the unit to the position
        Args:
            destination: The pixel on which the unit will be drawn.
        """
        current_position = self.sprite.rect.center
        if current_position != destination:
            x, y = utils.geom.vectorize(current_position, destination)
            self.sprite.rect.move_ip(x, y)

    def move(self, destination_offset) -> None:
        """
        Translate the unit by the given offset.
        Args:
            destination_offset: The translation offset to perform
        """
        self.sprite.rect.move_ip(destination_offset[0], destination_offset[1])
