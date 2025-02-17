"""The Polygon class."""

from collections.abc import Sequence
from functools import cached_property
from math import sin, cos, pi as PI
from typing import Any

from .algorithms import monotone_triangulation
from .matrix import Matrix
from .simplex import PointsMatrix, Point2D, Segment


class Polygon(PointsMatrix):
    """A (potentially non-convex) polygon."""

    def __init__(self, points):
        # type: (Sequence[Point2D]) -> None
        super().__init__(Matrix(tuple(
            (point.x, point.y, 0, 1)
            for point in points
        )))
        # partition
        self.triangles = monotone_triangulation(points)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return (self.points,)

    @cached_property
    def points(self):
        # type: () -> tuple[Point2D, ...]
        """Return the points of the polygon."""
        return tuple(
            Point2D(row[0], row[1])
            for row in self.matrix.rows
        )

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
    def area(self):
        # type: () -> float
        """Calculate the area of the polygon."""
        return sum(triangle.area for triangle in self.triangles)

    @cached_property
    def centroid(self):
        # type: () -> Point2D
        """Calculate the centroid of the polygon."""
        total_area = 0 # type: float
        centroid = Point2D()
        for triangle in self.triangles:
            total_area += triangle.area
            centroid += triangle.area * triangle.centroid
        result = centroid / total_area
        return Point2D(result.x, result.y)

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
