"""A basic window for basic drawing."""

from math import sin, cos

from .color import Color
from .simplex import PointsMatrix
from .game import Game
from .game_object import GameObject


class DummyGameObject(GameObject):
    """A dummy game object to hold a static geometry."""

    def __init__(self, polygon, fill_color=None, line_color=None):
        # type: (PointsMatrix, Color, Color) -> None
        super().__init__()
        self.points_matrix = polygon
        self.fill_color = fill_color
        self.line_color = line_color


class BasicWindow(Game):
    """A basic window for drawing static geometries."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        super().__init__(width, height)
        for keysym in ['w', 's', 'a', 'd', 'e', 'q', 'space', 'r', 'f']:
            self.bind_key(f'<{keysym}>', self.key_callback)

    def add_geometry(self, polygon, fill_color=None, line_color=None):
        # type: (PointsMatrix, Color, Color) -> None
        """Add a geometry to be drawn."""
        self.add_object(DummyGameObject(
            polygon,
            fill_color=fill_color,
            line_color=line_color,
        ))

    def key_callback(self, keysym):
        # type: (str) -> None
        """Deal with key presses."""
        translation = 25 / self.camera.zoom
        if keysym == 'w':
            self.camera.move_by(translation * sin(-self.camera.radians), translation * cos(-self.camera.radians))
        elif keysym == 's':
            self.camera.move_by(-translation * sin(-self.camera.radians), -translation * cos(-self.camera.radians))
        elif keysym == 'a':
            self.camera.move_by(-translation * cos(self.camera.radians), -translation * sin(self.camera.radians))
        elif keysym == 'd':
            self.camera.move_by(translation * cos(self.camera.radians), translation * sin(self.camera.radians))
        elif keysym == 'q':
            self.camera.rotate_by(0.125)
        elif keysym == 'e':
            self.camera.rotate_by(-0.125)
        elif keysym == 'space':
            self.camera.move_to(0, 0)
            self.camera.rotate_to(0)
            self.camera.zoom_level = 0
        elif keysym == 'r':
            self.camera.zoom_level += 1
        elif keysym == 'f':
            self.camera.zoom_level -= 1
