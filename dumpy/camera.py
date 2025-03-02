"""A 2D camera."""

from functools import lru_cache

from .canvas import Canvas
from .color import Color
from .game_object import GameObject
from .matrix import Matrix
from .simplex import PointsMatrix
from .transform import Transform


@lru_cache
def projection_matrix(width, height, x, y, theta, zoom): # pylint: disable = too-many-positional-arguments
    # type: (int, int, float, float, float, float) -> Matrix
    """Create the projection matrix."""
    return (
        Transform(width // 2, height // 2).matrix
        @ Transform(x, y, theta, 1 / zoom).matrix.inverse.y_reflection
    )


class Camera(GameObject):
    """A 2D camera."""

    def __init__(self, canvas, zoom_level=0):
        # type: (Canvas, int) -> None
        """Initialize the Camera."""
        super().__init__()
        self.canvas = canvas
        self.zoom_level = zoom_level
        self.origin_transform = Transform(
            self.canvas.width // 2,
            self.canvas.height // 2,
        )

    @property
    def zoom(self):
        # type: () -> float
        """Get the zoom level."""
        return 1.25 ** self.zoom_level

    def _project(self, matrix):
        # type: (Matrix) -> Matrix
        """Project to screen coordinates.

        Because this project involves flipping the y-axis, it cannot be
        represented as a Transform, and the underlying matrix must be used
        instead. The creation of the matrix is put in a separate function to
        take advantage of caching.
        """
        return (
            projection_matrix(
                self.canvas.width,
                self.canvas.height,
                self.position.x,
                self.position.y,
                self.theta,
                self.zoom,
            ) @ matrix.transpose
        ).transpose

    def draw_points_matrix(self, points_matrix, fill_color=None, line_color=None):
        # type: (PointsMatrix, Color, Color) -> None
        """Draw a PointsMatrix."""
        matrix = self._project(points_matrix.matrix)
        if matrix.height == 1:
            self.canvas.draw_pixel(
                (matrix[0][0], matrix[0][1]),
                fill_color=fill_color,
            )
        elif matrix.height == 2:
            self.canvas.draw_line(
                (matrix[0][0], matrix[0][1]),
                (matrix[1][0], matrix[2][1]),
                line_color=line_color,
            )
        else:
            self.canvas.draw_poly(
                tuple((row[0], row[1]) for row in matrix.rows),
                fill_color=fill_color,
                line_color=line_color,
            )
