"""Tests for canvas.py."""

from itertools import batched, product
from pathlib import Path
from typing import Iterator

from PIL import Image, ImageGrab

from dumpy.canvas import Canvas
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
    canvas.display_page()
    canvas.canvas.update()
    x0 = canvas.tk.winfo_rootx() + canvas.canvas.winfo_x() + 1
    y0 = canvas.tk.winfo_rooty() + canvas.canvas.winfo_y() + 1
    x1 = x0 + canvas.canvas.winfo_width() - 2
    y1 = y0 + canvas.canvas.winfo_height() - 2
    canvas.tk.destroy()
    return ImageGrab.grab().crop((x0, y0, x1, y1))


def check_image(image, filename):
    # type: (Image, str) -> None
    """Check that a canvas matches the file."""
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
    canvas = Canvas(3, 3, 'test')
    canvas.draw_pixel((1, 1))
    check_image(canvas.image, 'canvas_pixel_test.ppm')


def test_canvas_line():
    # type: () -> None
    """Test drawing a line."""
    # test all combinations of primes
    sizes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for width, height in product(sizes, repeat=2):
        canvas = Canvas(width, height, 'test')
        # draw NW to SE diagonal
        canvas.draw_line(
            (0, 0),
            (width - 1, height - 1),
        )
        # draw SW to NE diagonal
        canvas.draw_line(
            (0, height - 1),
            (width - 1, 0),
        )
        # get the resulting image
        image = canvas.image.convert('RGB')
        # identify the drawn pixels
        top_left_quadrant = set()
        all_quadrants = set()
        for row in range(height):
            for col in range(width):
                pixel = image.getpixel((col, row))
                if sum(pixel) / 3 >= 128:
                    continue
                all_quadrants.add((col, row))
                if col <= width / 2 and row <= height / 2:
                    top_left_quadrant.add((col, row))
        # test horizontal and vertical symmetry
        for col, row in sorted(top_left_quadrant):
            assert (width - col - 1, row) in all_quadrants
            assert (col, height - row - 1) in all_quadrants
            assert (width - col - 1, height - row - 1) in all_quadrants


def test_canvas_rect():
    # type: () -> None
    """Test drawing a filled rectangle."""
    canvas = Canvas(5, 5, 'test')
    canvas.draw_rect(
        (1, 1),
        (3, 3),
        fill_color=Color.from_hex('#000000'),
    )
    check_image(canvas.image, 'canvas_rect_test.ppm')


def test_canvas_rect_outline():
    # type: () -> None
    """Test drawing a rectangle outline."""
    canvas = Canvas(5, 5, 'test')
    canvas.draw_rect(
        (1, 1),
        (3, 3),
        line_color=Color.from_hex('#000000'),
    )
    check_image(canvas.image, 'canvas_rect_outline_test.ppm')


def test_canvas_display():
    # type: () -> None
    canvas = Canvas(3, 3, 'test')
    canvas.draw_pixel((1, 0))
    canvas.draw_pixel((2, 1))
    canvas.draw_pixel((0, 2))
    canvas.draw_pixel((1, 2))
    canvas.draw_pixel((2, 2))
    image = grab_screen(canvas)
    check_image(canvas.image, 'canvas_display_test.ppm')
