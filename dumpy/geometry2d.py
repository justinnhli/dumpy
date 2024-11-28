"""2D geometry objects."""

from typing import Optional

from .matrix import Matrix, Point2D


class Segment:
    """A line segment."""

    def __init__(self, point1, point2):
        # type: (Matrix, Matrix) -> None
        if (point1.x, point1.y) > (point2.x, point2.y):
            point1, point2 = point2, point1
        self.point1 = point1
        self.point2 = point2

    @property
    def min_x(self):
        # type: () -> float
        """The smaller x-coordinate."""
        return min(self.point1.x, self.point2.x)

    @property
    def max_x(self):
        # type: () -> float
        """The larger x-coordinate."""
        return max(self.point1.x, self.point2.x)

    @property
    def min_y(self):
        # type: () -> float
        """The smaller y-coordinate."""
        return min(self.point1.y, self.point2.y)

    @property
    def max_y(self):
        # type: () -> float
        """The larger y-coordinate."""
        return max(self.point1.y, self.point2.y)

    @property
    def slope(self):
        # type: () -> float
        """The slope of the segment."""
        denominator = self.point2.x - self.point1.x
        if denominator == 0:
            return float('Inf')
        else:
            return (self.point2.y - self.point1.y) / denominator

    def __str__(self):
        # type: () -> str
        return f'Segment({self.point1}, {self.point2})'

    def is_parallel(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is parallel."""
        return self.slope == other.slope

    @staticmethod
    def _orientation(p1, p2, p3):
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

    def contains(self, point, include_end=True):
        # type: (Point2D, bool) -> bool
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
        o1 = Segment._orientation(self.point1, other.point1, other.point2)
        o2 = Segment._orientation(self.point2, other.point1, other.point2)
        o3 = Segment._orientation(other.point1, self.point1, self.point2)
        o4 = Segment._orientation(other.point2, self.point1, self.point2)
        # general case: no co-linearity
        if 0 not in (o1, o2, o3, o4):
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
