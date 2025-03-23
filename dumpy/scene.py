"""A scene of objects."""

from collections import defaultdict
from itertools import product, combinations
from typing import Callable

from .camera import Camera
from .game_object import GameObject


CollisionCallback = Callable[[], None] # FIXME


class Scene:

    def __init__(self):
        # type: () -> None
        """Initialize the Scene."""
        self.objects = [] # type: list[GameObject]
        self.groups = defaultdict(set) # type: dict[int, set[str]]
        self.collision_groups = {} # type: dict[frozenset[str], CollisionCallback]

    def add(self, game_object, *groups):
        # type: (GameObject, *str) -> None
        """Add an object to the scene."""
        self.objects.append(game_object)
        self.groups[id(game_object)] |= set(groups)

    def get_in_view(self, camera):
        # type: (Camera) -> list[GameObject]
        """Get all objects in view of the camera."""
        return self.objects # FIXME

    def register_collision(self, group1, group2, callback):
        # type: (str, str, CollisionCallback) -> None
        """Register two object groups for collision detection."""
        self.collision_groups[frozenset([group1, group2])] = callback

    def trigger_collisions(self):
        # type: () -> None
        """Trigger object collision callbacks."""
        # FIXME horribly inefficient
        for obj1, obj2 in combinations(self.objects, 2):
            if not self.colliding(obj1, obj2):
                continue
            for group1, group2 in product(self.groups[id(obj1)], self.groups[id(obj2)]):
                key = frozenset([group1, group2])
                if key in self.collision_groups:
                    self.collision_groups[key]()

    def colliding(self, obj1, obj2):
        # type: (GameObject, GameObject) -> bool
        """Determine if two objects are colliding."""
        return False # FIXME
