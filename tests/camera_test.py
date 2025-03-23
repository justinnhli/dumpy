"""Tests for camera.py."""

from dumpy.camera import Camera
from dumpy.canvas import Canvas
from dumpy.polygon import Polygon
from dumpy.simplex import Point2D

from image_test_utils import check_image


def test_canvas_pixel():
    # type: () -> None
    """Test drawing a pixel."""
    canvas = Canvas(3, 3, 'test')
    camera = Camera(canvas)
    camera.draw_points_matrix(Point2D(0, 0))
    check_image(canvas.image, 'canvas__pixel.ppm')


def test_canvas_rect():
    # type: () -> None
    """Test drawing a rectangle."""
    canvas = Canvas(5, 5, 'test')
    camera = Camera(canvas)
    camera.draw_points_matrix(Polygon.rectangle(2, 2))
    check_image(canvas.image, 'canvas__rect_outline.ppm')
