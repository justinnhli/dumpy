"""A canvas built in tk and Pillow."""

from tkinter import CENTER, Tk, Canvas as TKCanvas, Event, NW
from typing import Callable, Sequence

from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageTk import PhotoImage

from .color import Color

Tuple2D = tuple[float, float]


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

    def draw_pixel(self, point, color=None):
        # type: (Tuple2D, Color) -> None
        """Draw a pixel."""
        if color is None:
            color = Color(0, 0, 0)
        self.image.putpixel((round(point[0]), round(point[1])), color.to_rgba_tuple())

    def draw_line(self, point1, point2, line_color=None):
        # type: (Tuple2D, Tuple2D, Color) -> None
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
        # type: (Tuple2D, Tuple2D, Color, Color) -> None
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
        # type: (Sequence[Tuple2D], Color, Color) -> None
        """Draw a polygon."""
        fill_color, line_color = Canvas._set_default_colors(fill_color, line_color)
        self.draw.polygon(
            [(round(point[0]), round(point[1])) for point in points],
            outline=line_color.to_rgba_tuple(),
            fill=fill_color.to_rgba_tuple(),
            width=1,
        )

    def draw_text(self, point, text, anchor=None):
        # type: (Tuple2D, Color, Color) -> None
        """Draw text."""
        pass # FIXME

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
        self.image = Image.new(
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
            update_fn()
            self.display_page()
            self.tk.after(msecs, callback)

        return callback

    def start(self, update_fn=None, secs=0):
        # type: (Callable[[], None], float) -> None
        """Display the canvas."""
        self.canvas.focus_set()
        if update_fn is None:
            self.display_page()
        elif secs > 0:
            msecs = int(1000 * secs)
            self.tk.after(msecs, self._create_update_callback(update_fn, msecs))
        else:
            self.tk.after(0, update_fn)
        self.canvas.mainloop()

    # interaction functions

    def bind_key(self, key, callback):
        # type: (str, Callable[[Event[TKCanvas]], None]) -> None
        """Add a keybind."""
        if self.tk is None:
            self.create_tk()
        # FIXME need parameters for modifier keys
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
