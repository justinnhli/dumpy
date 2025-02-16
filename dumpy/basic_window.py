"""A basic window for basic drawing."""

from tkinter import Event

from .camera import Camera
from .canvas import Canvas
from .simplex import PointsMatrix


class BasicWindow:
    """A basic window for drawing static geometries."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        self.canvas = Canvas(width, height)
        self.camera = Camera(self.canvas)
        for key in ['w', 's', 'a', 'd', 'e', 'q', 'space', 'r', 'f']:
            self.canvas.bind_key(f'<{key}>', self.key_callback)
        self.points_matrixes = [] # type: list[PointsMatrix]

    def draw(self, geometry):
        # type: (PointsMatrix) -> None
        """Add a geometry to be drawn later."""
        self.points_matrixes.append(geometry)

    def _draw(self):
        # type: () -> None
        """Draw all geometries."""
        self.canvas.new_page()
        for points_matrix in self.points_matrixes:
            self.camera.draw_points_matrix(points_matrix)

    def start(self):
        # type: () -> None
        """Display the canvas."""
        self.canvas.start(self._draw, 1 / 25)

    def key_callback(self, event):
        # type: (Event) -> None
        """Deal with key presses."""
        translation = 25 / self.camera.zoom
        if event.keysym == 'w':
            self.camera.move_by(0, translation)
        elif event.keysym == 's':
            self.camera.move_by(0, -translation)
        elif event.keysym == 'a':
            self.camera.move_by(-translation, 0)
        elif event.keysym == 'd':
            self.camera.move_by(translation, 0)
        elif event.keysym == 'q':
            self.camera.rotate_by(0.125)
        elif event.keysym == 'e':
            self.camera.rotate_by(-0.125)
        elif event.keysym == 'space':
            self.camera.move_to(0, 0)
        elif event.keysym == 'r':
            self.camera.zoom_level -= 1
        elif event.keysym == 'f':
            self.camera.zoom_level += 1
