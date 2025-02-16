"""2D geometry primitives."""

from functools import cached_property
from math import atan2
from typing import Any, Optional, Iterator, Self

from .camera import Camera
from .matrix import Matrix, Point2D
from .metaprogramming import cached_class
from .mixins import Transform
from .root_class import RootClass


@cached_class
class PointsMatrix(RootClass):
    """Abstract class for a sequence of points."""

    def __init__(self, matrix):
        # type: (Matrix) -> None
        super().__init__()
        self.matrix = matrix

    def __round__(self, ndigits=0):
        # type: (int) -> Self
        return type(self).from_matrix(round(self.matrix, ndigits))

    def calculate_hash(self):
        # type: () -> int
        return hash(self.matrix)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return (self.matrix,)

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> PointsMatrix
        """Create the class from a matrix."""
        raise NotImplementedError()


@cached_class
class Segment:
    """A line segment."""

    def __init__(self, point1, point2):
        # type: (Matrix, Matrix) -> None
        self.point1 = point1
        self.point2 = point2
        self._hash = None

    @cached_property
    def min(self):
        # type: () -> Matrix
        """The "smaller" point."""
        if self.point1.to_tuple <= self.point2.to_tuple:
            return self.point1
        else:
            return self.point2

    @cached_property
    def max(self):
        # type: () -> Matrix
        """The "larger" point."""
        if self.point1.to_tuple <= self.point2.to_tuple:
            return self.point2
        else:
            return self.point1

    @cached_property
    def min_x(self):
        # type: () -> float
        """The smaller x-coordinate."""
        return self.point1.x

    @cached_property
    def max_x(self):
        # type: () -> float
        """The larger x-coordinate."""
        return self.point2.x

    @cached_property
    def min_y(self):
        # type: () -> float
        """The smaller y-coordinate."""
        return min(self.point1.y, self.point2.y)

    @cached_property
    def max_y(self):
        # type: () -> float
        """The larger y-coordinate."""
        return max(self.point1.y, self.point2.y)

    @cached_property
    def twin(self):
        # type: () -> Segment
        """The twin segment."""
        return Segment(self.point2, self.point1)

    @cached_property
    def slope(self):
        # type: () -> float
        """The slope of the segment."""
        denominator = self.point2.x - self.point1.x
        if denominator == 0:
            return float('Inf')
        else:
            return (self.point2.y - self.point1.y) / denominator

    def __hash__(self):
        # type: () -> int
        if not self._hash:
            self._hash = hash((self.point1, self.point2))
        return self._hash

    def __eq__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_components == other.to_components

    def __lt__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_components < other.to_components

    def __iter__(self):
        # type: () -> Iterator[Matrix]
        yield self.point1
        yield self.point2

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        components = ', '.join(repr(component) for component in self.to_components)
        return f'{type(self).__name__}({components})'

    def is_parallel(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is parallel."""
        return self.slope == other.slope

    def is_colinear(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is colinear."""
        return Segment(self.point1, other.point1).slope == self.slope == other.slope

    def is_kissing(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment intersects at an endpoint."""
        return (
            self.point1 in (other.point1, other.point2)
            or self.point2 in (other.point2, other.point2)
        )

    def is_overlapping(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment overlaps at more than one point."""
        return (
            self.is_colinear(other)
            and (
                self.contains(other.point1, include_end=False)
                or self.contains(other.point2, include_end=False)
                or other.contains(self.point1, include_end=False)
                or other.contains(self.point2, include_end=False)
            )
        )

    @staticmethod
    def _angle(p1, p2, p3):
        # type: (Matrix, Matrix, Matrix) -> float
        return atan2(p3.y - p2.y, p3.x - p2.x) - atan2(p1.y - p2.y, p1.x - p2.x)

    @staticmethod
    def _orientation(p1, p2, p3):
        # type: (Matrix, Matrix, Matrix) -> int
        """Determine the orientation going from p1 to p2 to p3."""
        val = (
            ((p2.y - p1.y) * (p3.x - p2.x))
            - ((p2.x - p1.x) * (p3.y - p2.y))
        )
        if val < 0: # counterclockwise
            return -1
        elif val > 0: # clockwise
            return 1
        else: # co-linear
            return 0

    def contains(self, point, include_end=True):
        # type: (Matrix, bool) -> bool
        """Return True if the point is on the segment."""
        if include_end:
            return (
                (point.x <= max(self.point1.x, self.point2.x))
                and (point.x >= min(self.point1.x, self.point2.x))
                and (point.y <= max(self.point1.y, self.point2.y))
                and (point.y >= min(self.point1.y, self.point2.y))
            )
        else:
            return (
                (point.x < max(self.point1.x, self.point2.x))
                and (point.x > min(self.point1.x, self.point2.x))
                and (point.y < max(self.point1.y, self.point2.y))
                and (point.y > min(self.point1.y, self.point2.y))
            )

    def intersect(self, other, include_end=True):
        # type: (Segment, bool) -> Optional[Matrix]
        """Find the intersection with another segment, if any."""
        bounding_box_overlaps = (
            (
                self.min_x <= other.min_x <= self.max_x
                or other.min_x <= self.min_x <= other.max_x
            ) and (
                self.min_y <= other.min_y <= self.max_y
                or other.min_y <= self.min_y <= other.max_y
            )
        )
        if not bounding_box_overlaps:
            return None
        o1 = Segment._orientation(self.point1, other.point1, other.point2)
        o2 = Segment._orientation(self.point2, other.point1, other.point2)
        o3 = Segment._orientation(other.point1, self.point1, self.point2)
        o4 = Segment._orientation(other.point2, self.point1, self.point2)
        # general case: no co-linearity
        if 0 not in (o1, o2, o3, o4):
            if self.is_parallel(other):
                return None
            vector1 = self.point2 - self.point1
            vector2 = other.point2 - other.point1
            perpendicular1 = Point2D(-vector2.y, vector2.x)
            proportion1 = (other.point1 - self.point1).dot(perpendicular1) / vector1.dot(perpendicular1)
            perpendicular2 = Point2D(-vector1.y, vector1.x)
            proportion2 = (self.point1 - other.point1).dot(perpendicular2) / vector2.dot(perpendicular2)
            if 0 <= proportion1 <= 1 and 0 <= proportion2 <= 1:
                if include_end or (proportion1 not in (0, 1) and proportion2 not in (0, 1)):
                    return self.point1 + vector1 * proportion1
            return None
        if not include_end:
            return None
        if o1 == 0 and other.contains(self.point1, include_end=True):
            # p1, q1 and p2 are collinear and p2 lies on segment p1q1
            return self.point1
        elif o2 == 0 and other.contains(self.point2, include_end=True):
            # p1, q1 and q2 are collinear and q2 lies on segment p1q1
            return self.point2
        elif o3 == 0 and self.contains(other.point1, include_end=True):
            # p2, q2 and p1 are collinear and p1 lies on segment p2q2
            return other.point1
        elif o4 == 0 and self.contains(other.point2, include_end=True):
            # p2, q2 and q1 are collinear and q1 lies on segment p2q2
            return other.point2
        else:
            return None

    def draw(self, camera, transform=None):
        # type: (Camera, Transform) -> None
        """Draw the segment."""
        if transform is None:
            transform = Transform()
        camera.draw_line(transform @ self.point1, transform @ self.point2)

    @cached_property
    def to_components(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.point1, self.point2

    @cached_property
    def to_tuple(self):
        # type: () -> tuple[Any, ...]
        """Convert to a tuple."""
        return tuple(component.to_tuple for component in self.to_components)

    @staticmethod
    def from_tuple(value):
        # type: () -> Segment
        """Create from a tuple."""
        return Segment(
            Matrix.from_tuple(value[0]),
            Matrix.from_tuple(value[1]),
        )


@cached_class
class Triangle:
    """A triangle."""

    def __init__(self, point1, point2, point3):
        # type: (Matrix, Matrix, Matrix) -> None
        points_list = [point1, point2, point3]
        if Segment._orientation(point1, point2, point3) != -1:
            raise ValueError(f'triangle is not counterclockwise: {points_list}')
        min_index = min(enumerate(points_list), key=(lambda pair: pair[1]))[0]
        self.points = tuple(points_list[min_index:] + points_list[:min_index])
        self._hash = None

    @cached_property
    def segments(self):
        # type: () -> tuple[Segment]
        point1, point2, point3 = self.points
        return (
            Segment(point1, point2),
            Segment(point2, point3),
            Segment(point3, point1),
        )

    @cached_property
    def area(self):
        # type: () -> float
        """The area of the Triangle."""
        point1, point2, point3 = self.points
        return abs(
            point1.x * (point2.y - point3.y)
            + point2.x * (point3.y - point1.y)
            + point3.x * (point1.y - point2.y)
        ) / 2

    @cached_property
    def centroid(self):
        # type: () -> Matrix
        """The centroid of the Triangle."""
        result = sum(self.points, start=Point2D()) / 3
        return Point2D(result.x, result.y)

    def __hash__(self):
        # type: () -> int
        if not self._hash:
            self._hash = hash((self.segment1, self.segment2, self.segment3))
        return self._hash

    def __eq__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_components == other.to_components

    def __lt__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_components < other.to_components

    def __iter__(self):
        # type: () -> Iterator[Segment]
        yield from self.points

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        components = ', '.join(repr(component) for component in self.to_components)
        return f'{type(self).__name__}({components})'

    def draw(self, camera, transform):
        # type: (Camera, Transform) -> None
        """Draw the triangle."""
        if transform is None:
            transform = Transform()
        camera.draw_poly([transform @ point for point in self.points])

    @cached_property
    def to_components(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.points

    @cached_property
    def to_tuple(self):
        # type: () -> tuple[Any, ...]
        """Convert to a tuple."""
        return tuple(component.to_tuple for component in self.to_components)

    @staticmethod
    def from_tuple(value):
        # type: () -> Triangle
        """Create from a tuple."""
        return Triangle(
            Matrix.from_tuple(value[0]),
            Matrix.from_tuple(value[1]),
            Matrix.from_tuple(value[2]),
        )

    @staticmethod
    def from_segments(segment1, segment2, segment3):
        return Triangle(
            segment1.point1,
            segment2.point1,
            segment3.point1,
        )
