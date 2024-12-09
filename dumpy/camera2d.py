"""A 2D camera."""

from typing import Any, Sequence

from .color import Color
from .canvas import Canvas
from .mixin2d import Transform2DMixIn
from .matrix import Point2D, Matrix


class Camera2D(Transform2DMixIn):
    """A 2D camera."""

    def __init__(self, canvas, *args, zoom_level=0, **kwargs):
        # type: (Canvas, Any, int, Any) -> None
        """Initialize the Camera2D."""
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.zoom_level = zoom_level

    @property
    def zoom(self):
        # type: () -> float
        """Get the zoom level."""
        return 1.25 ** self.zoom_level

    def _translate(self, point):
        # type: (Matrix) -> Matrix
        return Point2D(
            self.zoom * (point.x - self.position.x) + (self.canvas.size.x // 2),
            self.zoom * (-point.y + self.position.y) + (self.canvas.size.y // 2),
        )

    def draw_pixel(self, point, color=None):
        # type: (Matrix, Color) -> None
        """Draw a pixel."""
        self.canvas.draw_pixel(
            self._translate(point),
            color,
        )

    def draw_line(self, point1, point2, line_color=None):
        # type: (Matrix, Matrix, Color) -> None
        """Draw a line."""
        self.canvas.draw_line(
            self._translate(point1),
            self._translate(point2),
            line_color,
        )

    def draw_rect(self, point1, point2, fill_color=None, line_color=None):
        # type: (Matrix, Matrix, Color, Color) -> None
        """Draw a rectangle."""
        self.canvas.draw_rect(
            self._translate(point1),
            self._translate(point2),
            fill_color,
            line_color,
        )

    def draw_poly(self, points, fill_color=None, line_color=None):
        # type: (Sequence[Matrix], Color, Color) -> None
        """Draw a polygon."""
        self.canvas.draw_poly(
            [self._translate(point) for point in points],
            fill_color,
            line_color,
        )
