"""A basic window for basic drawing."""

from math import sin, cos

from .canvas import Input
from .color import Color
from .game import Game
from .game_object import GameObject
from .simplex import PointsMatrix, Point2D


class DummyGameObject(GameObject):
    """A dummy game object to hold a static geometry."""

    def __init__(self, polygon, fill_color=None, line_color=None):
        # type: (PointsMatrix, Color, Color) -> None
        """Initialize the DummyGameObject."""
        super().__init__()
        self.points_matrix = polygon
        self.fill_color = fill_color
        self.line_color = line_color


class BasicWindow(Game):
    """A basic window for drawing static geometries."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        """Initialize the BasicWindow."""
        super().__init__(width, height)
        for char in ['w', 's', 'a', 'd', 'e', 'q', ' ', 'r', 'f']:
            self.bind(Input(event_type='KeyPress', key_button=char), self.key_callback)

    def add_geometry(self, polygon, fill_color=None, line_color=None):
        # type: (PointsMatrix, Color, Color) -> None
        """Add a geometry to be drawn."""
        self.add_object(DummyGameObject(
            polygon,
            fill_color=fill_color,
            line_color=line_color,
        ))

    def key_callback(self, input_event, mouse_pos):
        # type: (Input, Point2D) -> None
        """Deal with key presses."""
        translation = 25 / self.camera.zoom
        if input_event.key_button == 'w':
            self.camera.move_by(translation * sin(-self.camera.radians), translation * cos(-self.camera.radians))
        elif input_event.key_button == 's':
            self.camera.move_by(-translation * sin(-self.camera.radians), -translation * cos(-self.camera.radians))
        elif input_event.key_button == 'a':
            self.camera.move_by(-translation * cos(self.camera.radians), -translation * sin(self.camera.radians))
        elif input_event.key_button == 'd':
            self.camera.move_by(translation * cos(self.camera.radians), translation * sin(self.camera.radians))
        elif input_event.key_button == 'q':
            self.camera.rotate_by(0.125)
        elif input_event.key_button == 'e':
            self.camera.rotate_by(-0.125)
        elif input_event.key_button == ' ':
            self.camera.move_to(0, 0)
            self.camera.rotate_to(0)
            self.camera.zoom_level = 0
        elif input_event.key_button == 'r':
            self.camera.zoom_level += 1
        elif input_event.key_button == 'f':
            self.camera.zoom_level -= 1
