"""The Color class."""

from typing import Any, Iterator

from ._okhsv import RGB as _RGB, HSV as _HSV
from ._okhsv import okhsv_to_rgb as _okhsv_to_rgb, rgb_to_okhsv as _rgb_to_okhsv


class Color:
    """A color, canonically represented as in OkHSVA."""

    # pylint: disable = invalid-name

    MAX_H = 360
    MAX_S = 100
    MAX_V = 100
    MAX_A = 256

    def __init__(self, h, s, v, a=1):
        # type: (float, float, float, float) -> None
        """Initialize the Color."""
        assert 0 <= h <= 1
        assert 0 <= s <= 1
        assert 0 <= v <= 1
        assert 0 <= a <= 1
        self.h = h
        self.s = s
        self.v = v
        self.a = a

    def __hash__(self):
        # type: () -> int
        return hash(self.to_hsva_tuple())

    def __eq__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_hsva_tuple() == other.to_hsva_tuple()

    def __lt__(self, other):
        # type: (Color) -> bool
        assert isinstance(other, type(self))
        return self.to_hsva_tuple() < other.to_hsva_tuple()

    def __iter__(self):
        # type: () -> Iterator[float]
        yield from self.to_hsva_tuple()

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return f'Color({self.h}, {self.s}, {self.v}, {self.a})'

    def to_hsva_tuple(self, integer=True):
        # type: (bool) -> tuple[float, float, float, float]
        """Convert the color to a HSVA tuple."""
        if integer:
            return (
                round(Color.MAX_H * self.h),
                round(Color.MAX_S * self.s),
                round(Color.MAX_V * self.v),
                round(Color.MAX_A * self.a),
            )
        else:
            return (self.h, self.s, self.v, self.a)

    def to_rgb_tuple(self, integer=True):
        # type: (bool) -> tuple[float, float, float]
        """Convert the color to a RGBA tuple."""
        return self.to_rgba_tuple(integer)[:3]

    def to_rgba_tuple(self, integer=True):
        # type: (bool) -> tuple[float, float, float, float]
        """Convert the color to a RGB tuple."""
        rgba = (*_okhsv_to_rgb(_HSV(self.h, self.s, self.v)), self.a)
        if integer:
            rgba = tuple(min(round(256 * x), 255) for x in rgba)
        return rgba

    def to_rgb_hex(self):
        # type: () -> str
        """Convert the color to a RGB hexcode."""
        return self.to_rgba_hex()[:7]

    def to_rgba_hex(self):
        # type: () -> str
        """Convert the color to a RGBA hexcode."""
        return '#' + ''.join(
            f'{n:02X}' for n in self.to_rgba_tuple(integer=True)
        )

    @staticmethod
    def from_rgba(r, g, b, a=1):
        # type: (float, float, float, float) -> Color
        """Create a color from RGB[A] values."""
        assert 0 <= r <= 1
        assert 0 <= g <= 1
        assert 0 <= b <= 1
        assert 0 <= a <= 1
        h, s, v = _rgb_to_okhsv(_RGB(r, g, b))
        return Color(
            min(h, 1),
            min(s, 1),
            min(v, 1),
            min(a, 1),
        )

    @staticmethod
    def from_hex(hexcode):
        # type: (str) -> Color
        """Create a color from a RGB[A] hexcode."""
        return Color.from_rgba(*(
            int(hexcode[i:i+2], 16) / 256
            for i in range(1, len(hexcode) - 1, 2)
        ))
