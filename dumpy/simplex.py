"""2D geometry primitives."""

from functools import cached_property
from math import atan2
from typing import Any, Union, Optional, Self

from .matrix import Matrix
from .metaprogramming import cached_class
from .root_class import RootClass
from .transform import Transform


class PointsMatrix(RootClass):
    """Abstract class for a sequence of points."""

    def __init__(self, matrix):
        # type: (Matrix) -> None
        super().__init__()
        self.matrix = matrix

    def __round__(self, ndigits=0):
        # type: (int) -> Self
        return type(self).from_matrix(round(self.matrix, ndigits))

    def __floor__(self):
        # type: () -> Self
        return type(self).from_matrix(self.matrix.__floor__())

    def __ceil__(self):
        # type: () -> Self
        return type(self).from_matrix(self.matrix.__ceil__())

    def __rmatmul__(self, other):
        # type: (Transform) -> Self
        assert isinstance(other, Transform)
        return type(self).from_matrix((other.matrix @ self.matrix.transpose).transpose)

    def calculate_hash(self):
        # type: () -> int
        return hash(self.matrix)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return (self.matrix,)

    @cached_property
    def x_reflection(self):
        # type: () -> Self
        """Reflect across the x-axis."""
        return type(self).from_matrix(Matrix(tuple(
            (-row[0], row[1], row[2], row[3])
            for row in self.matrix.rows
        )))

    @cached_property
    def y_reflection(self):
        # type: () -> Self
        """Reflect across the y-axis."""
        return type(self).from_matrix(Matrix(tuple(
            (row[0], -row[1], row[2], row[3])
            for row in self.matrix.rows
        )))

    @cached_property
    def z_reflection(self):
        # type: () -> Self
        """Reflect across the z-axis."""
        return type(self).from_matrix(Matrix(tuple(
            (row[0], row[1], -row[2], row[3])
            for row in self.matrix.rows
        )))

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> PointsMatrix
        """Create the class from a matrix."""
        raise NotImplementedError()


class Tuple2D(PointsMatrix):
    """Abstract class for 2D points and vectors."""

    def __init__(self, x, y, w):
        # type: (float, float, int) -> None
        super().__init__(Matrix(((x, y, 0, w),)))

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the initialization arguments."""
        return self.x, self.y, self.w

    @cached_property
    def x(self):
        # type: () -> float
        """Return the x component of the tuple."""
        return self.matrix.x

    @cached_property
    def y(self):
        # type: () -> float
        """Return the y component of the tuple."""
        return self.matrix.y

    @cached_property
    def w(self):
        # type: () -> float
        """Return the w component of the tuple."""
        return self.matrix.w

    def __sub__(self, other):
        # type: (Tuple2D) -> Vector2D
        assert isinstance(other, type(self))
        return Vector2D(self.x - other.x, self.y - other.y)

    def __mul__(self, other):
        # type: (Union[int, float]) -> Self
        return type(self).from_matrix(other * self.matrix)

    def __rmul__(self, other):
        # type: (Union[int, float]) -> Self
        return type(self).from_matrix(other * self.matrix)

    def __truediv__(self, other):
        # type: (float) -> Self
        return type(self).from_matrix((1 / other) * self.matrix)

    def dot(self, other):
        # type: (Any) -> float
        """Return the dot product."""
        assert isinstance(other, Tuple2D)
        return self.matrix.dot(other.matrix)

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Tuple2D
        return Tuple2D(
            matrix.rows[0][0], # x
            matrix.rows[0][1], # y
            matrix.rows[0][3], # w
        )


@cached_class
class Point2D(Tuple2D):
    """A 2D point."""

    def __init__(self, x=0, y=0):
        # type: (float, float) -> None
        super().__init__(x, y, 1)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return self.x, self.y

    def __add__(self, other):
        # type: (Vector2D) -> Point2D
        assert isinstance(other, Tuple2D)
        return Point2D(self.x + other.x, self.y + other.y)

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Point2D
        return Point2D(
            matrix.rows[0][0],
            matrix.rows[0][1],
        )


@cached_class
class Vector2D(Tuple2D):
    """A 2D Vector."""

    def __init__(self, x=0, y=0):
        # type: (float, float) -> None
        super().__init__(x, y, 0)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return self.x, self.y

    def __add__(self, other):
        # type: (Tuple2D) -> Tuple2D
        assert isinstance(other, Tuple2D)
        return type(other)(self.x + other.x, self.y + other.y)

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Vector2D
        return Vector2D(
            matrix.rows[0][0],
            matrix.rows[0][1],
        )


@cached_class
class Segment(PointsMatrix):
    """A line segment."""

    def __init__(self, point1, point2):
        # type: (Point2D, Point2D) -> None
        assert point1 != point2
        super().__init__(Matrix((
            (point1.x, point1.y, 0, 1),
            (point2.x, point2.y, 0, 1),
        )))

    @cached_property
    def point1(self):
        # type: () -> Point2D
        """The source point."""
        return Point2D(self.matrix.rows[0][0], self.matrix.rows[0][1])

    @cached_property
    def point2(self):
        # type: () -> Point2D
        """The destination point."""
        return Point2D(self.matrix.rows[1][0], self.matrix.rows[1][1])

    @cached_property
    def points(self):
        # type: () -> tuple[Point2D, Point2D]
        """Return the points of the segment."""
        return (self.point1, self.point2)

    @cached_property
    def min(self):
        # type: () -> Point2D
        """The "smaller" point."""
        if self.point1 <= self.point2:
            return self.point1
        else:
            return self.point2

    @cached_property
    def max(self):
        # type: () -> Point2D
        """The "larger" point."""
        if self.point1 <= self.point2:
            return self.point2
        else:
            return self.point1

    @cached_property
    def min_x(self):
        # type: () -> float
        """The smaller x-coordinate."""
        return min(self.point1.x, self.point2.x)

    @cached_property
    def max_x(self):
        # type: () -> float
        """The larger x-coordinate."""
        return max(self.point1.x, self.point2.x)

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

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.point1, self.point2

    def is_parallel(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is parallel."""
        crossmul1 = (self.point2.x - self.point1.x) * (other.point2.y - other.point1.y)
        crossmul2 = (other.point2.x - other.point1.x) * (self.point2.y - self.point1.y)
        return crossmul1 == crossmul2

    def is_colinear(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is colinear."""
        if not self.is_parallel(other):
            return False
        if self.point1 == other.point1:
            third_segment = Segment(self.point1, other.point2)
        else:
            third_segment = Segment(self.point1, other.point1)
        return self.is_parallel(third_segment)

    def is_kissing(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment intersects at an endpoint."""
        return (
            self.point1 in (other.point1, other.point2)
            or self.point2 in (other.point1, other.point2)
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

    def contains(self, point, include_end=True):
        # type: (Point2D, bool) -> bool
        """Return True if the point is on the segment."""
        if include_end:
            return (
                self.min_x <= point.x <= self.max_x
                and self.min_y <= point.y <= self.max_y
            )
        else:
            return (
                (
                    self.point1.x == self.point2.x
                    or self.min_x < point.x < self.max_x
                ) and (
                    self.point1.y == self.point2.y
                    or self.min_y < point.y < self.max_y
                )
            )

    def point_at(self, x):
        # type: (float) -> Point2D
        """Find the point at x."""
        assert self.min_x != self.max_x
        assert self.min_x <= x <= self.max_x, (self.min_x, x, self.max_x)
        if x == self.min_x:
            return self.min
        elif x == self.max_x:
            return self.max
        else:
            numerator = self.point2.y - self.point1.y
            denominator = self.point2.x - self.point1.x
            return Point2D(
                x,
                self.point1.y + (x - self.point1.x) * numerator / denominator,
            )

    def intersect(self, other, include_end=True):
        # type: (Segment, bool) -> Optional[Point2D]
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
        o1 = Segment.orientation(self.point1, other.point1, other.point2)
        o2 = Segment.orientation(self.point2, other.point1, other.point2)
        o3 = Segment.orientation(other.point1, self.point1, self.point2)
        o4 = Segment.orientation(other.point2, self.point1, self.point2)
        # general case: no co-linearity
        if 0 not in (o1, o2, o3, o4):
            if self.is_parallel(other):
                return None
            if self > other:
                return other.intersect(self)
            # calculate y=mx+b for both segments to solve for the intersection
            # avoid Segment.slope for better numeric stability
            diff1x = self.point2.x - self.point1.x
            diff1y = self.point2.y - self.point1.y
            diff2x = other.point2.x - other.point1.x
            diff2y = other.point2.y - other.point1.y
            x = (
                (
                    (other.point1.y - self.point1.y) * (diff1x * diff2x)
                    + (self.point1.x * diff1y * diff2x - other.point1.x * diff1x * diff2y)
                )
                / (diff1y * diff2x - diff2y * diff1x)
            )
            if not (self.min_x <= x <= self.max_x and other.min_x <= x <= other.max_x):
                return None
            # preferentially select the line to calculate the intersection from
            if diff1y == 0:
                result = self.point_at(x)
            elif diff2y == 0:
                result = other.point_at(x)
            elif diff1x != 0:
                result = self.point_at(x)
            else:
                result = other.point_at(x)
            if not (self.min_y <= result.y <= self.max_y and other.min_y <= result.y <= other.max_y):
                return None
            if not include_end and result in (self.point1, self.point2, other.point1, other.point2):
                return None
            else:
                return result
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

    @staticmethod
    def angle(p1, p2, p3):
        # type: (Point2D, Point2D, Point2D) -> float
        """Determine the angle going from p1 to p2 to p3."""
        return atan2(p3.y - p2.y, p3.x - p2.x) - atan2(p1.y - p2.y, p1.x - p2.x)

    @staticmethod
    def orientation(p1, p2, p3):
        # type: (Point2D, Point2D, Point2D) -> int
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

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Segment
        return Segment(
            Point2D(matrix.rows[0][0], matrix.rows[0][1]),
            Point2D(matrix.rows[1][0], matrix.rows[1][1]),
        )


@cached_class
class Triangle(PointsMatrix):
    """A triangle."""

    def __init__(self, point1, point2, point3):
        # type: (Point2D, Point2D, Point2D) -> None
        points_list = [point1, point2, point3]
        if Segment.orientation(point1, point2, point3) != -1:
            raise ValueError(f'triangle is not counterclockwise: {points_list}')
        super().__init__(Matrix((
            (point1.x, point1.y, 0, 1),
            (point2.x, point2.y, 0, 1),
            (point3.x, point3.y, 0, 1),
        )))

    @cached_property
    def point1(self):
        # type: () -> Point2D
        """Return the "first" point of the triangle."""
        return Point2D(self.matrix.rows[0][0], self.matrix.rows[0][1])

    @cached_property
    def point2(self):
        # type: () -> Point2D
        """Return the "second" point of the triangle."""
        return Point2D(self.matrix.rows[1][0], self.matrix.rows[1][1])

    @cached_property
    def point3(self):
        # type: () -> Point2D
        """Return the "third" point of the triangle."""
        return Point2D(self.matrix.rows[2][0], self.matrix.rows[2][1])

    @cached_property
    def points(self):
        # type: () -> tuple[Point2D, Point2D, Point2D]
        """Return the points of the triangle."""
        return (self.point1, self.point2, self.point3)

    @cached_property
    def segments(self):
        # type: () -> tuple[Segment, Segment, Segment]
        """Return the segments of the triangle."""
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
        # type: () -> Point2D
        """The centroid of the Triangle."""
        result = sum(self.points, start=Point2D()) / 3
        return Point2D(result.x, result.y)

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        return self.point1, self.point2, self.point3

    @staticmethod
    def from_matrix(matrix):
        # type: (Matrix) -> Triangle
        return Triangle(
            Point2D(matrix.rows[0][0], matrix.rows[0][1]),
            Point2D(matrix.rows[1][0], matrix.rows[1][1]),
            Point2D(matrix.rows[2][0], matrix.rows[2][1]),
        )

    @staticmethod
    def from_segments(segment1, segment2, segment3):
        # type: (Segment, Segment, Segment) -> Triangle
        """Create a Triangle from segments."""
        return Triangle(
            segment1.point1,
            segment2.point1,
            segment3.point1,
        )
