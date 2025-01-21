"""Tests for camera.py."""

from itertools import batched
from pathlib import Path

from dumpy.camera import Camera
from dumpy.canvas import Canvas
from dumpy.matrix import Point2D

from canvas_test import check_image


def test_canvas_pixel():
    # type: () -> None
    """Test drawing a pixel."""
    canvas = Canvas(Point2D(3, 3), 'test')
    camera = Camera(canvas)
    camera.draw_pixel(Point2D(0, 0))
    check_image(canvas.image, 'canvas_pixel_test.ppm')
