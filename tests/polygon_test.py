"""Tests for polygon.py."""

from dumpy.polygon import Polygon
from dumpy.simplex import Point2D


def test_polygon():
    polygon = Polygon.rectangle(2, 2)
    assert polygon.area == 4
    assert polygon.centroid == Point2D()
    assert Polygon(*polygon.init_args) == polygon
