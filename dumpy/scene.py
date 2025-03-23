"""A scene of objects."""

from collections import defaultdict

from .camera import Camera
from .game_object import GameObject


class Scene:

    def __init__(self):
        # type: () -> None
        """Initialize the Scene."""
        self.objects = [] # type: list[GameObject]
        self.groups = defaultdict(set) # type: dict[int, set[str]]

    def add(self, game_object, *groups):
        # type: (GameObject, *str) -> None
        """Add an object to the scene."""
        self.objects.append(game_object)
        self.groups[id(game_object)] |= set(groups)

    def get_in_view(self, camera):
        # type: (Camera) -> list[GameObject]
        """Get all objects in view of the camera."""
        return self.objects # FIXME
