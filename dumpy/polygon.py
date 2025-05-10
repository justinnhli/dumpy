"""The Polygon class."""

from functools import cached_property
from math import sin, cos, pi as PI
from typing import Any

from .algorithms import monotone_triangulation
from .matrix import Matrix
from .metaprogramming import cached_class
from .simplex import PointsMatrix, Point2D, Vector2D, Segment


@cached_class
class Polygon(PointsMatrix):
    """A (potentially non-convex) polygon."""

    def __init__(self, points):
        # type: (tuple[Point2D, ...]) -> None
        # rotate points so the minimum point is first
        min_index = min(enumerate(points), key=(lambda pair: pair[1]))[0] # pylint: disable = superfluous-parens
        points = points[min_index:] + points[:min_index]
        super().__init__(Matrix(tuple(
            (point.x, point.y, 0, 1)
            for point in points
        )))

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return (self.points,)

    @cached_property
    def segments(self):
        # type: () -> tuple[Segment, ...]
        """Return the segments of the polygon."""
        points = self.points + (self.points[0],)
        return tuple(
            Segment(point1, point2)
            for point1, point2 in zip(points[:-1], points[1:])
        )

    @cached_property
    def triangles(self):
        # type: () -> tuple[Triangle, ...]
        """Return the triangles of the polygon."""
        return monotone_triangulation(self.points)

    @cached_property
    def area(self):
        # type: () -> float
        """Calculate the area of the polygon."""
        return sum(triangle.area for triangle in self.triangles)

    @cached_property
    def centroid(self):
        # type: () -> Point2D
        """Calculate the centroid of the polygon."""
        total_area = 0 # type: float
        centroid = Vector2D()
        for triangle in self.triangles:
            total_area += triangle.area
            centroid += triangle.area * triangle.centroid.to_vector()
        return (centroid / total_area).to_point()

    def union(self, *polygons):
        # type: (*Polygon) -> Polygon
        """Create the union of polygons."""
        raise NotImplementedError()

    def difference(self, *polygons):
        # type: (*Polygon) -> Polygon
        """Create the difference of polygons."""
        raise NotImplementedError()

    def intersection(self, *polygons):
        # type: (*Polygon) -> Polygon
        """Create the intersection of polygons."""
        raise NotImplementedError()

    @staticmethod
    def rectangle(width, height):
        # type: (float, float) -> Polygon
        """Create a rectangle."""
        half_width = width / 2
        half_height = height / 2
        points = (
            Point2D(-half_width, half_height),
            Point2D(-half_width, -half_height),
            Point2D(half_width, -half_height),
            Point2D(half_width, half_height),
        )
        return Polygon(points)

    @staticmethod
    def ellipse(width_radius, height_radius, num_points=40):
        # type: (float, float, int) -> Polygon
        """Create a ellipse."""
        step = PI / (num_points / 2)
        return Polygon(tuple(
            Point2D(width_radius * cos(i * step), height_radius * sin(i * step))
            for i in range(num_points)
        ))

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Polygon
        return Polygon(tuple(
            Point2D(row[0], row[1])
            for row in matrix.rows
        ))
