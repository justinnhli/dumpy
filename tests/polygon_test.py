"""Tests for polygon.py."""

from dumpy.polygon import Polygon
from dumpy.matrix import Point2D


def test_polygon():
    polygon = Polygon.rectangle(2, 2)
    assert polygon.area == 4
    assert polygon.centroid == Point2D()
    assert Polygon.from_tuple(polygon.to_tuple) == polygon
    assert polygon == Polygon([
        Point2D(0, 1), Point2D(-1, 1), Point2D(-1, 0), Point2D(-1, -1),
        Point2D(0, -1), Point2D(1, -1), Point2D(1, 0), Point2D(1, 1),
    ])
