"""Tests for polygon.py."""

from dumpy.polygon import Polygon
from dumpy.simplex import Point2D, Segment


def test_polygon():
    # type: () -> None
    """Test Polygon."""
    rectangle = Polygon.rectangle(2, 2)
    assert rectangle.area == 4
    assert rectangle.centroid == Point2D()
    ellipse = round(Polygon.ellipse(20, 10, num_points=4), 3)
    point1 = Point2D(-20, 0)
    point2 = Point2D(-0, -10)
    point3 = Point2D(20, 0)
    point4 = Point2D(0, 10)
    assert ellipse.points == (
        point1, point2, point3, point4
    )
    assert ellipse.segments == (
        Segment(point1, point2),
        Segment(point2, point3),
        Segment(point3, point4),
        Segment(point4, point1),
    )
