"""The Polygon class."""

from collections.abc import Sequence
from functools import cached_property
from math import sin, cos, pi as PI
from typing import Any

from .camera import Camera
from .matrix import Matrix, Point2D
from .mixins import TransformMixIn, Transform
from .simplex import Segment
from .algorithms import monotone_triangulation


class Polygon(TransformMixIn):
    """A (potentially non-convex) polygon."""

    def __init__(self, points, *args, **kwargs):
        # type: (Sequence[Matrix], Any, Any) -> None
        super().__init__(*args, **kwargs)
        # remove colinear points
        self.points = Polygon._simplify(points)
        # partition
        self.triangles = monotone_triangulation(self.points)
        self._hash = None

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
        return self.to_components == other.to_components

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

    def draw(self, camera, transform=None):
        # type: (Camera, Transform) -> None
        """Abstract method for drawing."""
        if transform is None:
            transform = Transform()
        for triangle in self.triangles:
            triangle.draw(camera, transform)

    @staticmethod
    def _simplify(points):
        # type: (Sequence[Matrix]) -> list[Matrix]
        """Remove colinear points.

        >>> points = [(0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (1, 1)]
        >>> all(
        ...     len(Polygon(
        ...         [Point2D(*point) for point in (points[i:] + points[:i])]
        ...     ).children[0].points) == 4
        ...     for i in range(len(points))
        ... )
        True

        >>> points = [(0, 1), (-0.5, 0.5), (-1, 0), (-0.5, -0.5), (0, -1), (0.5, -0.5), (1, 0), (0.5, 0.5)]
        >>> all(
        ...     len(Polygon(
        ...         [Point2D(*point) for point in (points[i:] + points[:i])]
        ...     ).children[0].points) == 4
        ...     for i in range(len(points))
        ... )
        True
        """
        angles = [
            Segment._orientation(
                points[i - 1],
                points[i],
                points[i + 1],
            )
            for i in range(-1, len(points) - 1)
        ]
        angles = angles[1:] + [angles[0]]
        return tuple(
            point for point, angle in zip(points, angles)
            if angle != 0 # FIXME use a more meaningful test
        )

    @staticmethod
    def rectangle(width, height, *args, **kwargs):
        # type: (float, float, *Any, **Any) -> Polygon
        """Create a rectangle."""
        half_width = width / 2
        half_height = height / 2
        points = [
            Point2D(-half_width, half_height),
            Point2D(-half_width, -half_height),
            Point2D(half_width, -half_height),
            Point2D(half_width, half_height),
        ]
        return Polygon(points, *args, **kwargs)

    @staticmethod
    def ellipse(width_radius, height_radius, *args, num_points=40, **kwargs):
        # type: (float, float, Any, int, Any) -> Polygon
        """Create a ellipse."""
        step = PI / (num_points / 2)
        return Polygon(
            [
                Point2D(width_radius * cos(i * step), height_radius * sin(i * step))
                for i in range(num_points)
            ],
            *args,
            **kwargs
        )

    @cached_property
    def to_components(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.points

    @cached_property
    def to_tuple(self):
        # type: () -> tuple[...]
        """Convert to a tuple."""
        return tuple(point.to_tuple for point in self.points)

    @staticmethod
    def from_tuple(value):
        # type: (tuple[...]) -> Polygon
        """Create from a tuple."""
        return Polygon([Matrix.from_tuple(point) for point in value])
