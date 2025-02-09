"""A Matrix class."""

# pylint: disable = too-many-lines

from functools import lru_cache as cache, cached_property
from math import sqrt, isclose, sin, cos
from typing import Any, Union, Sequence

from .metaprogramming import cached_class


EPSILON = 0.00001


@cached_class
class Matrix: # pylint: disable = too-many-public-methods
    """A matrix."""

    def __init__(self, values):
        # type: (tuple[tuple[float, ...], ...]) -> None
        """Initialize a matrix."""
        self.rows = values
        self.height = len(values)
        self.width = len(values[0])

    @cached_property
    def cols(self):
        # type: () -> tuple[tuple[float, ...], ...]
        """Get the columns of the matrix."""
        return tuple(
            tuple(self.rows[r][c] for r in range(self.height))
            for c in range(self.width)
        )

    @cached_property
    def is_tuple(self):
        # type: () -> bool
        """Return True if the matrix is a 4-tuple."""
        return self.height == 1 and self.width == 4

    @cached_property
    def is_vector(self):
        # type: () -> bool
        """Return True if the matrix is a graphics vector."""
        return self.is_tuple and self.rows[0][3] == 0

    @cached_property
    def is_point(self):
        # type: () -> bool
        """Return True if the matrix is a graphics point."""
        return self.is_tuple and self.rows[0][3] == 1

    @cached_property
    def x(self):
        # type: () -> float
        """Return the x value of a 4-tuple."""
        return self.rows[0][0]

    @cached_property
    def y(self):
        # type: () -> float
        """Return the y value of a 4-tuple."""
        return self.rows[0][1]

    @cached_property
    def z(self):
        # type: () -> float
        """Return the z value of a 4-tuple."""
        return self.rows[0][2]

    @cached_property
    def w(self): # pylint: disable = invalid-name
        # type: () -> float
        """Return the w value of a 4-tuple."""
        return self.rows[0][3]

    @cached_property
    def magnitude(self):
        # type: () -> float
        """Return the magnitude of a 4-tuple."""
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    @cached_property
    def normalized(self):
        # type: () -> Matrix
        """Normalize a graphics point/vector."""
        magnitude = self.magnitude
        return Matrix(((
            self.x / magnitude,
            self.y / magnitude,
            self.z / magnitude,
            self.w,
        ),))

    @cached_property
    def transpose(self):
        # type: () -> Matrix
        """Transpose the matrix."""
        return Matrix(self.cols)

    @cached_property
    def x_reflection(self):
        # type: () -> Matrix
        """Reflect across the x-axis."""
        return Matrix((
            (-1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        )) @ self

    @cached_property
    def y_reflection(self):
        # type: () -> Matrix
        """Reflect across the y-axis."""
        return Matrix((
            (1, 0, 0, 0),
            (0, -1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        )) @ self

    @cached_property
    def z_reflection(self):
        # type: () -> Matrix
        """Reflect across the z-axis."""
        return Matrix((
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, -1, 0),
            (0, 0, 0, 1),
        )) @ self

    @cached_property
    def determinant(self):
        # type: () -> float
        """Calculate the determinant."""
        if self.height == 2 and self.width == 2:
            return self.rows[0][0] * self.rows[1][1] - self.rows[0][1] * self.rows[1][0]
        else:
            return sum(self.rows[0][i] * self.cofactor(0, i) for i in range(self.width))

    @cached_property
    def invertible(self):
        # type: () -> bool
        """Return True if the matrix is invertible."""
        return self.determinant != 0

    @cached_property
    def inverse(self):
        # type: () -> Matrix
        """Inverse the matrix."""
        result = []
        for r in range(self.height):
            result.append(tuple(self.cofactor(r, c) for c in range(self.width)))
        return Matrix(tuple(result)).transpose / self.determinant

    def __hash__(self):
        # type: () -> int
        return hash(self.to_tuple())

    def __eq__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return (
            self.height == other.height and self.width == other.width
            and all(
                isclose(self_val, other_val, abs_tol=EPSILON)
                for self_row, other_row in zip(self.rows, other.rows)
                for self_val, other_val in zip(self_row, other_row)
            )
        )

    def __lt__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.rows < other.rows

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        if self.is_tuple:
            vals = [str(abs(i) if i == 0 else i) for i in self.rows[0]]
            if self.is_vector:
                return f'Vector3D({", ".join(vals[:-1])})'
            elif self.is_point:
                return f'Point3D({", ".join(vals[:-1])})'
            else:
                return f'Tuple({", ".join(vals)})'
        else:
            return f'Matrix({self.rows})'

    def __round__(self, ndigits=None):
        # type: (int) -> Matrix
        return Matrix(tuple(
            tuple(round(val, ndigits) for val in row)
            for row in self.rows
        ))

    def __add__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix(tuple(
            tuple(val1 + val2 for val1, val2 in zip(row1, row2))
            for row1, row2 in zip(self.rows, other.rows)
        ))

    def __sub__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix(tuple(
            tuple(val1 - val2 for val1, val2 in zip(row1, row2))
            for row1, row2 in zip(self.rows, other.rows)
        ))

    def __neg__(self):
        # type: () -> Matrix
        return Matrix(tuple(
            tuple(-val for val in row)
            for row in self.rows
        ))

    def __mul__(self, other):
        # type: (Union[int, float]) -> Matrix
        return Matrix(tuple(
            tuple(val * other for val in row)
            for row in self.rows
        ))

    def __rmul__(self, other):
        # type: (Union[int, float]) -> Matrix
        return self * other

    def __truediv__(self, other):
        # type: (Union[int, float]) -> Matrix
        return self * (1 / other)

    def __matmul__(self, other):
        # type: (Matrix) -> Matrix
        is_tuple = False
        if other.is_tuple:
            other = other.transpose
            is_tuple = True
        result = []
        for r in range(self.height):
            row = self.rows[r]
            result_row = []
            for c in range(other.width):
                col = other.cols[c]
                result_row.append(sum(a * b for a, b in zip(row, col)))
            result.append(tuple(result_row))
        if is_tuple:
            return Matrix(tuple(result)).transpose
        else:
            return Matrix(tuple(result))

    def reflect(self, other):
        # type: (Matrix) -> Matrix
        """Reflect across another 4-tuple."""
        normal = other.normalized
        return self - normal * 2 * self.dot(normal)

    def dot(self, other):
        # type: (Matrix) -> float
        """Take the dot product with another 4-tuple."""
        return (self @ other.transpose).rows[0][0]

    def cross(self, other):
        # type: (Matrix) -> Matrix
        """Take the cross product with another matrix."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def submatrix(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> Matrix
        """Slice out a submatrix."""
        return Matrix(tuple(
            row[:dc] + row[dc + 1:]
            for r, row in enumerate(self.rows)
            if r != dr
        ))

    def minor(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> float
        """Calculate a minor."""
        return self.submatrix(dr, dc).determinant

    def cofactor(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> float
        """Calculate a cofactor."""
        if (dr + dc) % 2 == 0:
            return self.minor(dr, dc)
        else:
            return -self.minor(dr, dc) # pylint: disable = invalid-unary-operand-type

    def translate(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """Translate the matrix."""
        return Matrix((
            (1, 0, 0, x),
            (0, 1, 0, y),
            (0, 0, 1, z),
            (0, 0, 0, 1),
        )) @ self

    def scale(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """Scale the matrix."""
        return Matrix((
            (x, 0, 0, 0),
            (0, y, 0, 0),
            (0, 0, z, 0),
            (0, 0, 0, 1),
        )) @ self

    def rotate_x(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the x-axis."""
        return Matrix((
            (1, 0, 0, 0),
            (0, cos(r), -sin(r), 0),
            (0, sin(r), cos(r), 0),
            (0, 0, 0, 1),
        )) @ self

    def rotate_y(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the y-axis."""
        return Matrix((
            (cos(r), 0, sin(r), 0),
            (0, 1, 0, 0),
            (-sin(r), 0, cos(r), 0),
            (0, 0, 0, 1),
        )) @ self

    def rotate_z(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the z-axis."""
        return Matrix((
            (cos(r), -sin(r), 0, 0),
            (sin(r), cos(r), 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        )) @ self

    def shear(self, x_y, x_z, y_x, y_z, z_x, z_y):
        # pylint: disable = too-many-positional-arguments
        # type: (float, float, float, float, float, float) -> Matrix
        """Shear the matrix."""
        return Matrix((
            (1, x_y, x_z, 0),
            (y_x, 1, y_z, 0),
            (z_x, z_y, 1, 0),
            (0, 0, 0, 1),
        )) @ self

    def to_tuple(self):
        # type: () -> tuple[tuple[float, ...], ...]
        """Convert to a tuple."""
        return self.rows

    @staticmethod
    def from_tuple(values):
        # type: (tuple[...]) -> Matrix
        """Create from a tuple."""
        return Matrix(values)


def Vector3D(x=0, y=0, z=0): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    """Create a 4-tuple that represents a 3D vector."""
    return Matrix(((x, y, z, 0),))


def Point3D(x=0, y=0, z=0): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    """Create a 4-tuple that represents a 3D point."""
    return Matrix(((x, y, z, 1),))


def Vector2D(x=0, y=0): # pylint: disable = invalid-name
    # type: (float, float) -> Matrix
    """Create a 4-tuple that represents a 2D vector."""
    return Matrix(((x, y, 0, 0),))


def Point2D(x=0, y=0): # pylint: disable = invalid-name
    # type: (float, float) -> Matrix
    """Create a 4-tuple that represents a 2D point."""
    return Matrix(((x, y, 0, 1),))


@cache
def identity(size=4):
    # type: (int) -> Matrix
    """Create an identity matrix."""
    return Matrix(tuple(
        (i * (0.0,)) + (1.0,) + (size - i - 1) * (0.0,)
        for i in range(size)
    ))
