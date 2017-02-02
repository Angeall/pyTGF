"""
File containing the definition of a Unit.
"""

from copy import deepcopy
from queue import Queue, Empty
from typing import List

import pygame

from pytgf.characters.units import Particle
from pytgf.characters.units.sprite import UnitSprite

__author__ = 'Anthony Rouneau'


class Unit(Particle):
    """
    A unit is a Particle that can have its own Particles. (e.g. a Gunner that owns its fired bullets)
    """

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

    def kill(self) -> None:
        """
        Kills the unit and all its particle if "surviving particles" was set to False at the creation of this unit
        """
        super().kill()
        if not self.isAlive():
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
        if self._particlesQueue is not None:
            self._particlesQueue.put(particle)
        self._particlesList.append(particle)
        if particle.sprite is not None:
            self._particlesSpriteGroup.add(particle.sprite)

    def removeOldestParticle(self) -> None:
        """
        Removes the oldest particle belonging to this unit-
        """
        try:
            oldest_particle = self._particlesList.pop(0)
            oldest_particle.kill()
            if self._particlesQueue is not None:
                queue_first = self._particlesQueue.get_nowait()  # type: Particle
                assert queue_first is oldest_particle
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

    def hasParticle(self, particle: Particle) -> bool:
        """
        Checks if the given particle belongs to this unit

        Args:
            particle: The particle to check

        Returns: True if the given particle belongs to this unit
        """
        return particle in self._particlesList or (self._particlesSpriteGroup is not None and
                                                   self._particlesSpriteGroup.has(particle.sprite))

    def getParticles(self) -> List[Particle]:
        """
        Returns: A list containing all the particles of this unit
        """
        return self._particlesList

    def getParticlesSpriteGroup(self) -> pygame.sprite.Group:
        """
        Gets the "SpriteGroup" of this unit, including all of its particle. Can be used for pygame's collision check
        """
        return self._particlesSpriteGroup

    def isColliding(self, other_sprite_group) -> bool:
        """
        Returns True if this unit or any of its particle collide with the other unit or any of its particle.
        (Uses the pygame collision check)

        Args:
            other_sprite_group: The other Sprite group with which we want to check if there is a collision

        Returns: True if the two group are colliding, False otherwise
        """
        for sprite in other_sprite_group.sprites:  # type: pygame.sprite.Sprite
            if pygame.sprite.collide_rect(self.sprite, sprite):
                return True
        return False

    def __deepcopy__(self, memo={}):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            if k != "_drawable" and k != "_particlesQueue":
                value = deepcopy(v, memo)
            else:
                value = None
            setattr(result, k, value)
        return result