import pygame
from queue import Queue, Empty

from characters.particle import Particle
from characters.sprite import UnitSprite


class Unit(Particle):
    def __init__(self, sprite: UnitSprite=None, max_particles: int=-1):
        """
        Instantiates a unit in the game
        Args:
            sprite: The sprite to draw on the board
            max_particles: The maximum number of particles for this unit (-1 = infinite)
        """
        super().__init__(sprite)
        self._particlesSpriteGroup = pygame.sprite.Group()
        self._particlesQueue = Queue()
        self._maxParticles = max_particles

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the unit and its particles
        Args:
            surface: The surface the unit and its particle will be drawn on
        """
        #self._particlesSpriteGroup.draw(surface)
        super().draw(surface)

    def addParticle(self, particle: Particle) -> None:
        """
        Adds a particle linked to this unit
        Args:
            particle: the particle to add to this unit
        """
        if 0 <= self._maxParticles <= len(self._particlesSpriteGroup):
            self.removeOldestParticle()
        self._particlesQueue.put(particle)
        self._particlesSpriteGroup.add(particle.sprite)

    def removeOldestParticle(self) -> None:
        """
        Removes the oldest particle belonging to this unit
        """
        try:
            oldest_particle = self._particlesQueue.get_nowait()  # type: Particle
            oldest_particle.kill()
            self._particlesSpriteGroup.remove(oldest_particle.sprite)
        except Empty:
            pass

    def removeParticle(self, particle: Particle) -> None:
        """
        Removes the given particle from the belongings of this unit
        Args:
            particle: The particle to remove
        """
        temp_queue = Queue()
        try:
            while True:  # Will stop when the Empty exception comes out from the Queue
                current = self._particlesQueue.get_nowait()
                if current is not particle:
                    temp_queue.put(current)
        except Empty:
            pass
        finally:
            self._particlesQueue = temp_queue
            particle.kill()
            self._particlesSpriteGroup.remove(particle.sprite)

