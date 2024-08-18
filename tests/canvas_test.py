"""Tests for canvas.py."""

from itertools import batched
from pathlib import Path
from typing import Iterator

from PIL import Image, ImageGrab

from dumpy.canvas import Canvas
from dumpy.matrix import Point2D
from dumpy.color import Color


def ppm_value_generator(path):
    # type: (Path) -> Iterator[str]
    """Read from a ppm file one value at a time."""
    with path.open() as fd:
        for line in fd:
            yield from line.strip().split()


def read_ppm(path):
    # type: (Path) -> tuple[int, int, list[tuple[int, int, int]]]
    """Read an image from a ppm file."""
    # create the generator
    generator = ppm_value_generator(path)
    # read the magic number
    assert next(generator) == 'P3'
    # read the width and height
    width, height = int(next(generator)), int(next(generator))
    # read (and discard) the bit depth
    next(generator)
    # create the pixel map
    pixels = [
        (int(r), int(g), int(b))
        for r, g, b in batched(generator, n=3)
    ]
    return width, height, pixels


def grab_screen(canvas):
    # type: (Canvas) -> Image
    """Take a screenshot of a canvas."""
    x0 = canvas.tk.winfo_rootx() + canvas.canvas.winfo_x() + 1
    y0 = canvas.tk.winfo_rooty() + canvas.canvas.winfo_y() + 1
    x1 = x0 + canvas.canvas.winfo_width() - 2
    y1 = y0 + canvas.canvas.winfo_height() - 2
    return ImageGrab.grab().crop((x0, y0, x1, y1))


def assert_canvas(canvas, filename, write=False):
    # type: (Canvas, str, bool) -> None
    """Check that a canvas matches the file."""
    canvas.display_page()
    canvas.canvas.update()
    image = grab_screen(canvas)
    canvas.tk.destroy()
    pixels = image.getdata()
    ppm_path = Path(__file__).parent / 'canvas_test_images' / filename
    width, height, ppm_pixels = read_ppm(ppm_path)
    assert image.width == width
    assert image.height == height
    pixels = image.getdata()
    for x in range(width):
        for y in range(height):
            index = x * width + y
            assert pixels[index] == ppm_pixels[index]


def test_canvas_pixel():
    # type: () -> None
    """Test drawing a pixel."""
    canvas = Canvas(Point2D(3, 3), 'test')
    canvas.draw_pixel(Point2D(1, 1))
    assert_canvas(canvas, 'canvas_pixel_test.ppm')


def test_canvas_rect():
    # type: () -> None
    """Test drawing a filled rectangle."""
    canvas = Canvas(Point2D(5, 5), 'test')
    canvas.draw_rect(
        Point2D(1, 1),
        Point2D(3, 3),
        fill_color=Color.from_hex('#000000'),
    )
    assert_canvas(canvas, 'canvas_rect_test.ppm')


def test_canvas_rect_outline():
    # type: () -> None
    """Test drawing a rectangle outline."""
    canvas = Canvas(Point2D(5, 5), 'test')
    canvas.draw_rect(
        Point2D(1, 1),
        Point2D(3, 3),
        line_color=Color.from_hex('#000000'),
    )
    assert_canvas(canvas, 'canvas_rect_outline_test.ppm')


def test_new_page():
    # type: () -> None
    """Test new page clears the screen."""
    canvas = Canvas(Point2D(3, 3), 'test')
    canvas.draw_pixel(Point2D(1, 1))
    canvas.new_page()
    assert_canvas(canvas, 'canvas_new_page_test.ppm')
