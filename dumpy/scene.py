"""A scene of objects."""

from itertools import product, combinations
from typing import Iterator, Iterable

from .camera import Camera
from .game_object import GameObject


class Scene:
    """A scene of game objects."""

    def __init__(self):
        # type: () -> None
        """Initialize the Scene."""
        self.objects = [] # type: list[GameObject]
        self.collision_group_pairs = set() # type: set[tuple[str, str]]

    @property
    def collisions(self):
        # type: () -> Iterator[tuple[GameObject, GameObject, tuple[str, str]]]
        """Yield all collisions of registered group pairs."""
        # FIXME horribly inefficient
        for obj1, obj2 in combinations(self.objects, 2):
            if not obj1.is_colliding(obj2):
                continue
            for group1, group2 in product(obj1.collision_groups, obj2.collision_groups):
                key = (group1, group2)
                if key in self.collision_group_pairs:
                    yield obj1, obj2, key
                key = (group2, group1)
                if key in self.collision_group_pairs:
                    yield obj2, obj1, key

    def add(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the scene."""
        self.objects.append(game_object)

    def get_in_view(self, camera):
        # type: (Camera) -> list[GameObject]
        """Get all objects in view of the camera."""
        return self.objects # FIXME

    def set_collision_group_pairs(self, collision_pairs):
        # type: (Iterable[tuple[str, str]]) -> None
        """Set collision group pairs to detect."""
        for group_pair in collision_pairs:
            self.collision_group_pairs.add(group_pair)
