"""A canvas built in tk and Pillow."""

from tkinter import CENTER, Tk, Canvas as TKCanvas, Event, NW
from typing import Callable, Sequence

from PIL import Image
from PIL.ImageDraw import Draw
from PIL.ImageTk import PhotoImage

from .color import Color
from .matrix import Matrix, Point2D


class Canvas:
    """A TkCanvas backed by Pillow Image."""

    def __init__(self, size, title=''):
        # type: (Matrix, str) -> None
        """Initialize the Canvas."""
        self.size = size
        self.title = title
        self.image = None # type: Image
        self.draw = None # type: Draw
        self.new_page()
        # gets around weird casing in title
        # see https://bugs.python.org/issue13553
        self.tk = Tk(className=('\u200B' + self.title)) # pylint: disable = superfluous-parens
        self.tk.minsize(self.size.x, self.size.y)

        self.canvas = TKCanvas(
            self.tk,
            width=self.size.x, height=self.size.y,
            background='#FFFFFF',
        )
        self.canvas.place(relx=.5, rely=.5, anchor=CENTER)
        self.image_tk = PhotoImage(self.image)

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
        # type: (Matrix, Color) -> None
        """Draw a pixel."""
        if color is None:
            color = Color(0, 0, 0)
        self.image.putpixel((point.x, point.y), color.to_rgba_tuple())

    def draw_line(self, point1, point2, line_color=None):
        # type: (Matrix, Matrix, Color) -> None
        """Draw a line.

        This function draws the line twice, in opposite directions, to ensure
        symmetry.
        """
        _, line_color = Canvas._set_default_colors(None, line_color)
        self.draw.line(
            [(point1.x, point1.y), (point2.x, point2.y)],
            fill=line_color.to_rgba_tuple(),
            width=1,
        )
        self.draw.line(
            [(point2.x, point2.y), (point1.x, point1.y)],
            fill=line_color.to_rgba_tuple(),
            width=1,
        )

    def draw_rect(self, point1, point2, fill_color=None, line_color=None):
        # type: (Matrix, Matrix, Color, Color) -> None
        """Draw a rectangle."""
        self.draw_poly(
            [
                point1,
                Point2D(point1.x, point2.y),
                point2,
                Point2D(point2.x, point1.y),
            ],
            fill_color,
            line_color,
        )

    def draw_poly(self, points, fill_color=None, line_color=None):
        # type: (Sequence[Matrix], Color, Color) -> None
        """Draw a polygon."""
        fill_color, line_color = Canvas._set_default_colors(fill_color, line_color)
        self.draw.polygon(
            [(point.x, point.y) for point in points],
            outline=line_color.to_rgba_tuple(),
            fill=fill_color.to_rgba_tuple(),
            width=1,
        )

    def draw_oval(self, point1, point2, fill_color=None, line_color=None):
        # type: (Matrix, Matrix, Color, Color) -> None
        """Draw an oval."""
        fill_color, line_color = Canvas._set_default_colors(fill_color, line_color)
        self.draw.ellipse(
            [(point1.x, point1.y), (point2.x, point2.y)],
            outline=line_color.to_rgba_tuple(),
            fill=fill_color.to_rgba_tuple(),
            width=1,
        )

    def draw_text(self, point, text, anchor=None):
        # type: (Matrix, Color, Color) -> None
        """Draw text."""
        pass # FIXME

    def new_page(self):
        # type: () -> None
        """Clear the image buffer.

        Note that the Image is created RGB but the Draw is created RGBA. This is
        necessary for transparency to work when drawing. See:
        https://github.com/python-pillow/Pillow/issues/2496#issuecomment-1814380516
        """
        self.image = Image.new(
            mode='RGB',
            size=(self.size.x, self.size.y),
            color='#FFFFFFFF',
        )
        self.draw = Draw(self.image, 'RGBA')

    def display_page(self):
        # type: () -> None
        """Draw the page to the canvas."""
        self.image_tk = PhotoImage(self.image)
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
        # FIXME need parameters for modifier keys
        self.canvas.bind(key, callback)

    def bind_mouse_click(self, button, callback):
        # type: (str, Callable[[Event[TKCanvas]], None]) -> None
        """Bind a mouse click."""
        if button == 'left':
            self.canvas.bind('<Button-1>', callback)
        elif button == 'middle':
            raise NotImplementedError()
        elif button == 'right':
            self.canvas.bind('<Button-2>', callback)

    def bind_mouse_movement(self, callback):
        # type: (Callable[[Event[TKCanvas]], None]) -> None
        """Bind mouse movement."""
        self.canvas.bind('<Motion>', callback)
