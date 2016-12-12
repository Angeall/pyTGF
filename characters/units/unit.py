import pygame
from queue import Queue, Empty

from characters.particle import Particle
from characters.sprite import UnitSprite


class Unit(Particle):
    def __init__(self, sprite: UnitSprite=None, max_particles: int=-1, nb_lives: int=1,
                 surviving_particles: bool=False):
        """
        Instantiates a unit in the game
        Args:
            sprite: The sprite to draw on the board
            max_particles: The maximum number of particles for this unit (-1 = infinite)
            nb_lives: The number of lives this unit has before it dies
            surviving_particles: If true, the particles of this unit won't die with this unit
        """
        super().__init__(sprite, nb_lives=nb_lives)
        self.survivingParticles = surviving_particles
        self._particlesSpriteGroup = pygame.sprite.Group()
        self._particlesQueue = Queue()
        self._particlesList = []
        self._maxParticles = max_particles

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the unit and its particles
        Args:
            surface: The surface the unit and its particle will be drawn on
        """
        super().draw(surface)
        self._particlesSpriteGroup.draw(surface)

    def kill(self):
        super().kill()
        if not self.survivingParticles:
            while len(self._particlesSpriteGroup) != 0:
                self.removeOldestParticle()

    def addParticle(self, particle: Particle) -> None:
        """
        Adds a particle linked to this unit
        Args:
            particle: the particle to add to this unit
        """
        if 0 <= self._maxParticles <= len(self._particlesList):
            self.removeOldestParticle()
        self._particlesQueue.put(particle)
        self._particlesList.append(particle)
        if particle.sprite is not None:
            self._particlesSpriteGroup.add(particle.sprite)

    def removeOldestParticle(self) -> None:
        """
        Removes the oldest particle belonging to this unit-
        """
        try:
            oldest_particle = self._particlesQueue.get_nowait()  # type: Particle
            assert oldest_particle is self._particlesList[0]
            self._particlesList = self._particlesList[1:]
            oldest_particle.kill()
            if oldest_particle.sprite is not None:
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
            self._particlesList.remove(particle)
            self._particlesQueue = temp_queue
            particle.kill()
            if particle.sprite is not None:
                self._particlesSpriteGroup.remove(particle.sprite)

    def hasParticle(self, particle: Particle):
        """
        Checks if the given particle beloings to this unit
        Args:
            particle: The particle to check

        Returns: True if the given particle belongs to this unit
        """
        return self._particlesSpriteGroup.has(particle.sprite) or particle in self._particlesList

    def getParticlesSpriteGroup(self):
        return self._particlesSpriteGroup

    def isColliding(self, other_sprite_group) -> bool:
        for sprite in other_sprite_group.sprites:  # type: pygame.sprite.Sprite
            if pygame.sprite.collide_rect(self.sprite, sprite):
                return True
        return False
