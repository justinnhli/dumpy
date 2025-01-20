"""A basic window for basic drawing."""

from math import pi as PI
from tkinter import Event

from .camera import Camera
from .canvas import Canvas
from .matrix import Point2D, Vector2D
from .mixins import Transform, TransformMixIn


class BasicWindow:
    """A basic window for drawing static geometries."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        self.canvas = Canvas(Point2D(width, height))
        self.camera = Camera(self.canvas)
        for key in ['w', 's', 'a', 'd', 'e', 'q', 'space', 'r', 'f']:
            self.canvas.bind_key(f'<{key}>', self.key_callback)
        self.geometries = [] # type: list[TransformMixIn]

    def draw(self, geometry):
        # type: (TransformMixIn) -> None
        """Add a geometry to be drawn later."""
        self.geometries.append(geometry)

    def _draw(self):
        # type: () -> None
        """Draw all geometries."""
        self.canvas.new_page()
        for geometry in self.geometries:
            geometry.draw(self.camera)

    def start(self):
        # type: () -> None
        """Display the canvas."""
        self.canvas.start(self._draw, 1 / 25)

    def key_callback(self, event):
        # type: (Event) -> None
        """Deal with key presses."""
        translation = 25 / self.camera.zoom
        if event.keysym == 'w':
            self.camera.move(Transform(Vector2D(0, translation)))
        elif event.keysym == 's':
            self.camera.move(Transform(Vector2D(0, -translation)))
        elif event.keysym == 'a':
            self.camera.move(Transform(Vector2D(-translation, 0)))
        elif event.keysym == 'd':
            self.camera.move(Transform(Vector2D(translation, 0)))
        elif event.keysym == 'q':
            self.camera.move(Transform(rotation=0.125))
        elif event.keysym == 'e':
            self.camera.move(Transform(rotation=-0.125))
        elif event.keysym == 'space':
            self.camera.move_to(Transform())
        elif event.keysym == 'r':
            self.camera.zoom_level -= 1
        elif event.keysym == 'f':
            self.camera.zoom_level += 1
