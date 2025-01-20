"""A 2D camera."""

from typing import Any, Sequence

from .canvas import Canvas
from .color import Color
from .matrix import Matrix, Point2D
from .mixins import Transform, TransformMixIn


class Camera(TransformMixIn):
    """A 2D camera."""

    def __init__(self, canvas, *args, zoom_level=0, **kwargs):
        # type: (Canvas, Any, int, Any) -> None
        """Initialize the Camera."""
        super().__init__(*args, **kwargs)
        self.canvas = canvas
        self.zoom_level = zoom_level
        self.origin_transform = Transform(Point2D(
            self.canvas.size.x // 2,
            self.canvas.size.y // 2,
        ))

    @property
    def zoom(self):
        # type: () -> float
        """Get the zoom level."""
        return 1.25 ** self.zoom_level

    def _translate(self, point):
        # type: (Matrix) -> Matrix
        transform_matrix = (
            self.transform.matrix
            .scale(self.zoom, self.zoom, self.zoom)
            .y_reflection
        )
        return self.origin_transform @ transform_matrix @ point

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
