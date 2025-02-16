"""The Polygon class."""

from collections.abc import Sequence
from functools import cached_property
from math import sin, cos, pi as PI
from typing import Any

from .algorithms import monotone_triangulation
from .matrix import Matrix
from .simplex import PointsMatrix, Point2D, Segment
from .transform import Transform


class Polygon(PointsMatrix):
    """A (potentially non-convex) polygon."""

    def __init__(self, points):
        # type: (Sequence[Matrix], Any, Any) -> None
        super().__init__(Matrix(tuple(
            (point.x, point.y, 0, 1)
            for point in points
        )))
        # partition
        self.triangles = monotone_triangulation(points)

    @cached_property
    def area(self):
        # type: () -> float
        """Calculate the area of the polygon."""
        return sum(triangle.area for triangle in self.triangles)

    @cached_property
    def centroid(self):
        # type: () -> Matrix
        """Calculate the centroid of the polygon."""
        total_area = 0
        centroid = Point2D()
        for triangle in self.triangles:
            total_area += triangle.area
            centroid += triangle.area * triangle.centroid
        result = centroid / total_area
        return Point2D(result.x, result.y)

    def __hash__(self):
        # type: () -> int
        if not self._hash:
            self._hash = hash(self.points)
        return self._hash

    def __eq__(self, other):
        assert isinstance(other, type(self))
        return self.init_args == other.init_args

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
        return Polygon((
            Point2D(width_radius * cos(i * step), height_radius * sin(i * step))
            for i in range(num_points)
        ))

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return (self.points,)
