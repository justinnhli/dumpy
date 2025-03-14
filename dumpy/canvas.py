"""A canvas built in tk and Pillow."""

from tkinter import CENTER, Tk, Canvas as TKCanvas, Event, NW
from typing import Callable, Sequence

from PIL.Image import Image, new as new_image
from PIL.ImageDraw import Draw
from PIL.ImageTk import PhotoImage

from .color import Color

_CHAR_KEYSYM_MAP = {
    ' ': 'space',
    '!': 'exclam',
    '"': 'quotedbl',
    '#': 'numbersign',
    '$': 'dollar',
    '%': 'percent',
    '&': 'ampersand',
    '\'': 'apostrophe',
    '(': 'parenleft',
    ')': 'parenright',
    '*': 'asterisk',
    '+': 'plus',
    ',': 'comma',
    '-': 'minus',
    '.': 'period',
    '/': 'slash',
    ':': 'colon',
    ';': 'semicolon',
    '<': 'less',
    '=': 'equal',
    '>': 'greater',
    '?': 'question',
    '@': 'at',
    '[': 'bracketleft',
    '\\': 'backslash',
    ']': 'bracketright',
    '^': 'asciicircum',
    '_': 'underscore',
    '`': 'grave',
    '{': 'braceleft',
    '|': 'bar',
    '}': 'braceright',
    '~': 'asciitilde',
}
_CHAR_KEYSYMS = set(_CHAR_KEYSYM_MAP.values())
_CONTROL_KEYSYMS = set([
    'Escape',
    'F1', 'F2', 'F3', 'F4', 'F5', 'F6',
    'F7', 'F8', 'F9', 'F10', 'F11', 'F12',
    'BackSpace', 'Tab', 'Return',
    'Insert', 'Delete', 'Home', 'End', 'Prior', 'Next',
    'Up', 'Left', 'Down', 'Right',
])
_ABSTRACT_KEYSYMS = set([
    'KeyPress', 'KeyRelease', 'Key'
])


FloatCoord = tuple[float, float]


def build_key_pattern(char_or_keysym, shift=False, control=False):
    # type: (str, bool, bool) -> KeyPattern
    if len(char_or_keysym) == 1:
        shift = False
        if char_or_keysym in _CHAR_KEYSYM_MAP:
            keysym = _CHAR_KEYSYM_MAP[char_or_keysym]
        elif char_or_keysym.isascii() and char_or_keysym.isalpha():
            keysym = char_or_keysym
        else:
            raise ValueError(f'unrecognized character: "{char_or_keysym}"')
    elif char_or_keysym in _CONTROL_KEYSYMS:
        keysym = char_or_keysym
    else:
        raise ValueError(f'unrecognized keysym: "{char_or_keysym}"')
    modifiers = ''
    if control:
        modifiers += 'Control-'
    if shift:
        modifiers += 'Shift-'
    return f'<{modifiers}{keysym}>'


def valid_key_pattern(key_pattern):
    # type: (str) -> bool
    if key_pattern[0] != '<' or key_pattern[-1] != '>':
        return False
    *modifiers, keysym = key_pattern[1:-1].split('-')
    valid_modifiers = set(['Control', 'Shift'])
    # FIXME does order matter?
    if not all(modifier in valid_modifiers for modifier in modifiers):
        return False
    if len(keysym) == 1:
        return keysym.isascii() and keysym.isalpha()
    else:
        return (
            keysym in _CHAR_KEYSYMS
            or keysym in _CONTROL_KEYSYMS
            or keysym in _ABSTRACT_KEYSYMS
        )


class Canvas:
    """A TkCanvas backed by Pillow Image."""

    def __init__(self, width, height, title=''):
        # type: (int, int, str) -> None
        """Initialize the Canvas."""
        self.width = width
        self.height = height
        self.title = title
        self.image = None # type: Image
        self.draw = None # type: Draw
        self.new_page()
        self.tk = None # type: Tk
        self.canvas = None # type: TKCanvas
        self.image_tk = None # type: PhotoImage

    # drawing functions

    @staticmethod
    def _set_default_colors(fill_color, line_color):
        # type: (Color, Color) -> tuple[Color, Color]
        if line_color is None:
            if fill_color is None:
                line_color = Color(0, 0, 0, 1)
                fill_color = Color(0, 0, 0, 0)
            else:
                line_color = fill_color
        elif fill_color is None:
            fill_color = Color(0, 0, 0, 0)
        return fill_color, line_color

    def draw_pixel(self, point, fill_color=None):
        # type: (FloatCoord, Color) -> None
        """Draw a pixel."""
        if fill_color is None:
            fill_color = Color(0, 0, 0)
        self.image.putpixel((round(point[0]), round(point[1])), fill_color.to_rgba_tuple())

    def draw_line(self, point1, point2, line_color=None):
        # type: (FloatCoord, FloatCoord, Color) -> None
        """Draw a line.

        This function draws the line twice, in opposite directions, to ensure
        symmetry.
        """
        point1_x = round(point1[0])
        point1_y = round(point1[1])
        point2_x = round(point2[0])
        point2_y = round(point2[1])
        _, line_color = Canvas._set_default_colors(None, line_color)
        self.draw.line(
            [(point1_x, point1_y), (point2_x, point2_y)],
            fill=line_color.to_rgba_tuple(),
            width=1,
        )
        self.draw.line(
            [(point2_x, point2_y), (point1_x, point1_y)],
            fill=line_color.to_rgba_tuple(),
            width=1,
        )

    def draw_rect(self, point1, point2, fill_color=None, line_color=None):
        # type: (FloatCoord, FloatCoord, Color, Color) -> None
        """Draw a rectangle."""
        self.draw_poly(
            [
                point1,
                (point1[0], point2[1]),
                point2,
                (point2[0], point1[1]),
            ],
            fill_color,
            line_color,
        )

    def draw_poly(self, points, fill_color=None, line_color=None):
        # type: (Sequence[FloatCoord], Color, Color) -> None
        """Draw a polygon."""
        fill_color, line_color = Canvas._set_default_colors(fill_color, line_color)
        self.draw.polygon(
            [(round(point[0]), round(point[1])) for point in points],
            outline=line_color.to_rgba_tuple(),
            fill=fill_color.to_rgba_tuple(),
            width=1,
        )

    def draw_text(self, point, text, anchor=None):
        # type: (FloatCoord, Color, Color) -> None
        """Draw text."""
        pass # FIXME

    # interaction functions

    def bind_key(self, key, callback):
        # type: (str, Callable[[Event[TKCanvas]], None]) -> None
        """Add a keybind."""
        if self.tk is None:
            self.create_tk()
        assert valid_key_pattern(key), key
        self.canvas.bind(key, callback)

    def bind_mouse_click(self, button, callback):
        # type: (str, Callable[[Event[TKCanvas]], None]) -> None
        """Bind a mouse click."""
        if self.tk is None:
            self.create_tk()
        if button == 'left':
            self.canvas.bind('<Button-1>', callback)
        elif button == 'middle':
            raise NotImplementedError()
        elif button == 'right':
            self.canvas.bind('<Button-2>', callback)

    def bind_mouse_movement(self, callback):
        # type: (Callable[[Event[TKCanvas]], None]) -> None
        """Bind mouse movement."""
        if self.tk is None:
            self.create_tk()
        self.canvas.bind('<Motion>', callback)

    # pipeline functions

    def create_tk(self):
        # type: () -> None
        """Create the Tk window."""
        # gets around weird casing in title
        # see https://bugs.python.org/issue13553
        self.tk = Tk(className=('\u200B' + self.title)) # pylint: disable = superfluous-parens
        self.tk.minsize(self.width, self.height)
        self.canvas = TKCanvas(
            self.tk,
            width=self.width, height=self.height,
            background='#FFFFFF',
        )
        self.canvas.place(relx=.5, rely=.5, anchor=CENTER)
        self.image_tk = PhotoImage(self.image, master=self.tk)

    def new_page(self):
        # type: () -> None
        """Clear the image buffer.

        Note that the Image is created RGB but the Draw is created RGBA. This is
        necessary for transparency to work when drawing. See:
        https://github.com/python-pillow/Pillow/issues/2496#issuecomment-1814380516
        """
        self.image = new_image(
            mode='RGB',
            size=(self.width, self.height),
            color='#FFFFFFFF',
        )
        self.draw = Draw(self.image, 'RGBA')

    def display_page(self):
        # type: () -> None
        """Draw the page to the canvas."""
        if self.tk is None:
            self.create_tk()
        self.image_tk = PhotoImage(self.image, master=self.tk)
        self.canvas.create_image(
            1, 1,
            anchor=NW,
            image=self.image_tk,
        )

    def _create_update_callback(self, update_fn, msecs):
        # type: (Callable[[], None], int) -> Callable[[], None]
        """Create the wrapped update callback function."""

        def callback():
            # type: () -> None
            self.new_page()
            update_fn()
            self.display_page()
            self.tk.after(msecs, callback)

        return callback

    def start(self, update_fn, msecs):
        # type: (Callable[[], None], int) -> None
        """Display the canvas."""
        self.canvas.focus_set()
        self.tk.after(msecs, self._create_update_callback(update_fn, msecs))
        self.canvas.mainloop()
