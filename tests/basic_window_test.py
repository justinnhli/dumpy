"""Tests for basic_window.py."""

from math import sqrt

from dumpy.basic_window import BasicWindow
from dumpy.color import Color
from dumpy.polygon import Polygon
from dumpy.simplex import Point2D
from dumpy.transform import Transform

from image_test_utils import check_image


def create_einstein():
    # type: () -> tuple[Polygon, Polygon, Polygon, Polygon]
    """Create the Einstein tile."""
    width = 100
    left_hexagon = Polygon.ellipse(width, width, num_points=6)
    down_hexagon = (
        Transform(
            x=3 * width / 2,
            y=-sqrt(3) * width / 2,
        ) @ left_hexagon
    )
    up_hexagon = (
        Transform(
            x=3 * width / 2,
            y=sqrt(3) * width / 2,
        ) @ left_hexagon
    )
    # build the einstein tile
    einstein = Polygon((
        left_hexagon.points[0] + (left_hexagon.points[1] - left_hexagon.points[0]) / 2,
        left_hexagon.points[1],
        left_hexagon.points[2],
        left_hexagon.points[2] + (left_hexagon.points[3] - left_hexagon.points[2]) / 2,
        Point2D(3 * width / 2, -sqrt(3) * width / 2),
        down_hexagon.points[3] + (down_hexagon.points[4] - down_hexagon.points[3]) / 2,
        down_hexagon.points[4],
        down_hexagon.points[4] + (down_hexagon.points[5] - down_hexagon.points[4]) / 2,
        Point2D(3 * width / 2, sqrt(3) * width / 2),
        up_hexagon.points[5] + (up_hexagon.points[0] - up_hexagon.points[5]) / 2,
        up_hexagon.points[0],
        left_hexagon.points[4] + (left_hexagon.points[5] - left_hexagon.points[4]) / 2,
        Point2D(),
    ))
    return left_hexagon, down_hexagon, up_hexagon, einstein


def test_rectangle():
    # type: () -> None
    """Draw a basic rectangle."""
    # create and display the window
    window = BasicWindow(5, 5)
    window.add_geometry(Polygon.rectangle(2, 2))
    window.dispatch_tick()
    check_image(window.canvas.image, 'basic_window__rectangle.ppm')


def test_einstein():
    # type: () -> None
    """Draw and center the Einstein tile."""
    left_hexagon, down_hexagon, up_hexagon, einstein = create_einstein()
    window = BasicWindow(600, 400)
    window.add_geometry(left_hexagon)
    window.add_geometry(down_hexagon)
    window.add_geometry(up_hexagon)
    window.add_geometry(einstein, line_color=Color(0, 1, 1))
    window.camera.move_to(einstein.centroid.x, einstein.centroid.y)
    window.dispatch_tick()
    check_image(window.canvas.image, 'basic_window__einstein.ppm')
