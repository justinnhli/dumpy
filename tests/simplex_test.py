"""Tests for simplex.py."""

from dumpy.matrix import Point2D
from dumpy.simplex import Segment, Triangle


def test_segment():
    # at most one point of intersection, include_end=True
    segments = [
        # vertical second segment
        (Segment(Point2D(0, 2), Point2D(0, 4)), (Point2D(0, 2), None)), # parallel, co-linear, end-end
        (Segment(Point2D(1, 2), Point2D(1, 4)), (None, None)), # parallel, not co-linear, not intersecting
        (Segment(Point2D(1, 1), Point2D(1, 3)), (None, None)), # parallel, not co-linear, not intersecting
        (Segment(Point2D(1, 0), Point2D(1, 2)), (None, None)), # parallel, not co-linear, not intersecting
        # horizontal second segment
        (Segment(Point2D(-1, 3), Point2D(1, 3)), (None, None)), # not parallel, not co-linear, not intersecting
        (Segment(Point2D(-1, 2), Point2D(1, 2)), (Point2D(0, 2), None)), # not parallel, co-linear, middle-end
        (Segment(Point2D(-1, 1), Point2D(1, 1)), (Point2D(0, 1), Point2D(0, 1))), # not parallel, not co-linear, middle-middle
        (Segment(Point2D(0, 3), Point2D(2, 3)), (None, None)), # not parallel, not co-linear, not intersecting
        (Segment(Point2D(0, 2), Point2D(2, 2)), (Point2D(0, 2), None)), # not parallel, co-linear, end-end
        (Segment(Point2D(0, 1), Point2D(2, 1)), (Point2D(0, 1), None)), # not parallel, co-linear, middle-end
    ]
    segment1 = Segment(Point2D(0, 0), Point2D(0, 2))
    for segment2, expecteds in segments:
        for expected, include_end in zip(expecteds, (True, False)):
            answer12 = segment1.intersect(segment2, include_end=include_end)
            answer21 = segment2.intersect(segment1, include_end=include_end)
            if expected is None:
                assert answer12 is None
                assert answer21 is None
            else:
                assert answer12 is not None
                assert answer21 is not None
                assert answer12 == expected
                assert answer21 == expected
    # more than one point of intersection
    segment2 = Segment(Point2D(0, 1), Point2D(0, 3))
    for answer in [segment1.intersect(segment2), segment2.intersect(segment1)]:
        assert answer.x == 0 and 1 <= answer.y <= 2
    segment2 = Segment(Point2D(0, 0), Point2D(0, 2))
    for answer in [segment1.intersect(segment2), segment2.intersect(segment1)]:
        assert answer.x == 0 and 0 <= answer.y <= 2
    # bounding box intersects but not segments
    segment1 = Segment(Point2D(0, 4), Point2D(4, 0))
    segment2 = Segment(Point2D(0, 0), Point2D(1, 1))
    assert segment1.intersect(segment2) is None
    assert segment2.intersect(segment1) is None
    # bug 2024-12-28
    segment1 = Segment(Point2D(3, 3), Point2D(4, 4))
    segment2 = Segment(Point2D(2, 2), Point2D(5, 5))
    assert segment1.is_overlapping(segment2) == segment2.is_overlapping(segment1) == True
    # bug 2024-12-28
    segment1 = Segment(Point2D(3, 4), Point2D(5, 2))
    segment2 = Segment(Point2D(2, 3), Point2D(4, 5))
    assert segment1.is_colinear(segment2) == segment2.is_colinear(segment1) == False
    assert segment1.is_overlapping(segment2) == segment2.is_overlapping(segment1) == False


def test_triangle():
    triangle = Triangle.from_points(
        Point2D(1, 2),
        Point2D(3, 4),
        Point2D(5, 6),
    )
    assert triangle == Triangle(
        Segment(Point2D(1, 2), Point2D(3, 4)),
        Segment(Point2D(3, 4), Point2D(5, 6)),
        Segment(Point2D(5, 6), Point2D(1, 2)),
    )
    assert tuple(triangle.points) == (Point2D(1, 2), Point2D(3, 4), Point2D(5, 6))
    assert triangle.segment1 == Segment(Point2D(1, 2), Point2D(3, 4))
    assert triangle.segment2 == Segment(Point2D(3, 4), Point2D(5, 6))
    assert triangle.segment3 == Segment(Point2D(5, 6), Point2D(1, 2))
    assert str(triangle) == 'Triangle(Point3D(1, 2, 0), Point3D(3, 4, 0), Point3D(5, 6, 0))'
    assert Triangle.from_tuple(triangle.to_tuple()) == triangle 

