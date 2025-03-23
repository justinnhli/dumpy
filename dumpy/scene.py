"""A scene of objects."""

from .camera import Camera
from .game_object import GameObject


class Scene:

    def __init__(self):
        # type: () -> None
        """Initialize the Scene."""
        self.objects = [] # type: list[GameObject]

    def add(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the scene."""
        self.objects.append(game_object)

    def get_in_view(self, camera):
        # type: (Camera) -> list[GameObject]
        """Get all objects in view of the camera."""
        return self.objects # FIXME
