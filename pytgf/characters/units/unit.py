"""
File containing the definition of a Unit.
"""

from copy import deepcopy
from queue import Queue, Empty
from typing import List

import pygame

from .entity import Entity
from .sprite import UnitSprite

__author__ = 'Anthony Rouneau'


class Unit(Entity):
    """
    A unit is an entity that can have its own entitys. (e.g. a Gunner that owns its fired bullets)
    """

    def __init__(self, player_number: int, sprite: UnitSprite=None, max_entities: int=-1, nb_lives: int=1,
                 surviving_entities: bool=False, speed: int=150):
        """
        Instantiates a unit in the game

        Args:
            sprite: The sprite to draw on the board
            max_entities: The maximum number of entities for this unit (-1 = infinite)
            nb_lives: The number of lives this unit has before it dies
            surviving_entities: If true, the entities of this unit won't die with this unit
        """
        super().__init__(sprite, nb_lives=nb_lives, speed=speed)
        self.survivingentitys = surviving_entities
        self.lastAction = None
        self.currentAction = None
        self.playerNumber = player_number
        self._entitiesSpriteGroup = pygame.sprite.Group()
        self._entitiesQueue = Queue()
        self._entitiesList = []
        self._maxentitys = max_entities

    def setLastAction(self, last_action):
        """
        Sets the last action of this unit
        
        Args:
            last_action: The last action performed by this unit 
        """
        self.lastAction = last_action

    def setCurrentAction(self, current_action):
        """
        Sets the current action of this unit
        
        Args:
            current_action: The action this unit is currently performing
        """
        self.currentAction = current_action

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draws the unit and its entities

        Args:
            surface: The surface the unit and its entity will be drawn on
        """
        super().draw(surface)
        self._entitiesSpriteGroup.draw(surface)

    def kill(self) -> None:
        """
        Kills the unit and all its entity if "surviving entities" was set to False at the creation of this unit
        """
        super().kill()
        if not self.isAlive():
            if not self.survivingentitys:
                while len(self._entitiesSpriteGroup) != 0:
                    self.removeOldestentity()

    def addentity(self, entity: Entity) -> None:
        """
        Adds an entity linked to this unit

        Args:
            entity: the entity to add to this unit
        """
        if 0 <= self._maxentitys <= len(self._entitiesList):
            self.removeOldestentity()
        if self._entitiesQueue is not None:
            self._entitiesQueue.put(entity)
        self._entitiesList.append(entity)
        if entity.sprite is not None:
            self._entitiesSpriteGroup.add(entity.sprite)

    def removeOldestentity(self) -> None:
        """
        Removes the oldest entity belonging to this unit-
        """
        try:
            oldest_entity = self._entitiesList.pop(0)
            oldest_entity.kill()
            if self._entitiesQueue is not None:
                queue_first = self._entitiesQueue.get_nowait()  # type: Entity
                assert queue_first is oldest_entity
            if oldest_entity.sprite is not None:
                self._entitiesSpriteGroup.remove(oldest_entity.sprite)
        except Empty:
            pass

    def removeentity(self, entity: Entity) -> None:
        """
        Removes the given entity from the belongings of this unit

        Args:
            entity: The entity to remove
        """
        temp_queue = Queue()
        try:
            while True:  # Will stop when the Empty exception comes out from the Queue
                current = self._entitiesQueue.get_nowait()
                if current is not entity:
                    temp_queue.put(current)
        except Empty:
            pass
        self._entitiesList.remove(entity)

        self._entitiesQueue = temp_queue
        entity.kill()
        if entity.sprite is not None:
            self._entitiesSpriteGroup.remove(entity.sprite)

    def hasentity(self, entity: Entity) -> bool:
        """
        Checks if the given entity belongs to this unit

        Args:
            entity: The entity to check

        Returns: True if the given entity belongs to this unit
        """
        return entity in self._entitiesList or (self._entitiesSpriteGroup is not None and
                                                   self._entitiesSpriteGroup.has(entity.sprite))

    def getentitys(self) -> List[Entity]:
        """
        Returns: A list containing all the entities of this unit
        """
        return self._entitiesList

    def getentitysSpriteGroup(self) -> pygame.sprite.Group:
        """
        Gets the "SpriteGroup" of this unit, including all of its entity. Can be used for pygame's collision check
        """
        return self._entitiesSpriteGroup

    def isColliding(self, other_sprite_group) -> bool:
        """
        Returns True if this unit or any of its entity collide with the other unit or any of its entity.
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
            if k != "_drawable" and k != "_entitiesQueue":
                value = deepcopy(v, memo)
            else:
                value = None
            setattr(result, k, value)
        return result
