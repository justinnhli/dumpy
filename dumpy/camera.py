"""A 2D camera."""

from .canvas import Canvas
from .game_object import GameObject
from .matrix import Matrix
from .simplex import PointsMatrix
from .transform import Transform


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

    def _translate(self, matrix):
        # type: (Matrix) -> Matrix
        transform_matrix = (
            self.transform.matrix
            .scale(self.zoom, self.zoom, self.zoom)
            .y_reflection
        )
        return self.origin_transform.matrix @ (transform_matrix @ matrix)

    def draw_points_matrix(self, points_matrix):
        # type: (PointsMatrix) -> None
        """Draw a PointsMatrix."""
        matrix = self._translate(points_matrix.matrix)
        if matrix.height == 1:
            print(matrix)
            self.canvas.draw_pixel((matrix[0][0], matrix[0][1]))
        elif matrix.height == 2:
            self.canvas.draw_line(
                (matrix[0][0], matrix[0][1]),
                (matrix[1][0], matrix[2][1]),
            )
        else:
            self.canvas.draw_poly(
                tuple((row[0], row[1]) for row in matrix.rows),
            )
