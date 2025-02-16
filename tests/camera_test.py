"""Tests for camera.py."""

from itertools import batched
from pathlib import Path

from dumpy.camera import Camera
from dumpy.canvas import Canvas
from dumpy.simplex import Point2D, Segment, Triangle

from canvas_test import check_image


def test_canvas_pixel():
    # type: () -> None
    """Test drawing a pixel."""
    canvas = Canvas(3, 3, 'test')
    camera = Camera(canvas)
    camera.draw_points_matrix(Point2D(0, 0))
    check_image(canvas.image, 'canvas_pixel_test.ppm')
