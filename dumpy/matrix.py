"""A Matrix class."""

# pylint: disable = too-many-lines

from math import sqrt, isclose, sin, cos
from typing import Any, Optional, Union


EPSILON = 0.00001


class Matrix: # pylint: disable = too-many-public-methods
    """A matrix.

    >>> Point3D(3, -2, 5) + Vector3D(-2, 3, 1)
    Point3D(1, 1, 6)

    >>> Point3D(3, 2, 1) - Point3D(5, 6, 7)
    Vector3D(-2, -4, -6)

    >>> Point3D(3, 2, 1) - Vector3D(5, 6, 7)
    Point3D(-2, -4, -6)

    >>> Vector3D(3, 2, 1) - Vector3D(5, 6, 7)
    Vector3D(-2, -4, -6)

    >>> Matrix([[1, -2, 3, -4]]) * 3.5 == Matrix([[3.5, -7, 10.5, -14]])
    True

    >>> 0.5 * Matrix([[1, -2, 3, -4]]) == Matrix([[0.5, -1, 1.5, -2]])
    True

    >>> Matrix([[1, -2, 3, -4]]) / 2 == Matrix([[0.5, -1, 1.5, -2]])
    True

    >>> Vector3D(1, 0, 0).magnitude == 1
    True

    >>> Vector3D(0, 1, 0).magnitude == 1
    True

    >>> Vector3D(0, 0, 1).magnitude == 1
    True

    >>> Vector3D(1, 2, 3).magnitude == sqrt(14)
    True

    >>> Vector3D(-1, -2, -3).magnitude == sqrt(14)
    True

    >>> Vector3D(4, 0, 0).normalize() == Vector3D(1, 0, 0)
    True

    >>> Vector3D(1, 2, 3).normalize().magnitude == 1
    True

    >>> Vector3D(1, 2, 3).dot(Vector3D(2, 3, 4))
    20

    >>> Vector3D(1, 2, 3).cross(Vector3D(2, 3, 4))
    Vector3D(-1, 2, -1)

    >>> Vector3D(2, 3, 4).cross(Vector3D(1, 2, 3))
    Vector3D(1, -2, 1)

    >>> m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    >>> m2 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    >>> m1 == m2
    True

    >>> m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    >>> m2 = Matrix([[2, 3, 4, 5], [6, 7, 8, 9], [8, 7, 6, 5], [4, 3, 2, 1]])
    >>> m1 == m2
    False

    >>> m1 = Matrix([[1, 2, 3, 4], [5, 6, 7, 8], [9, 8, 7, 6], [5, 4, 3, 2]])
    >>> m2 = Matrix([[-2, 1, 2, 3], [3, 2, 1, -1], [4, 3, 6, 5], [1, 2, 7, 8]])
    >>> m3 = Matrix([[20, 22, 50, 48], [44, 54, 114, 108], [40, 58, 110, 102], [16, 26, 46, 42]])
    >>> m1 @ m2 == m3
    True

    >>> m1 = Matrix([[1, 2, 3, 4], [2, 4, 4, 2], [8, 6, 4, 1], [0, 0, 0, 1]])
    >>> m1 @ Point3D(1, 2, 3)
    Point3D(18, 24, 33)

    >>> m1 = Matrix([[0, 1, 2, 4], [1, 2, 4, 8], [2, 4, 8, 16], [4, 8, 16, 32]])
    >>> m2 = identity()
    >>> m1 @ m2 == m1
    True

    >>> m1 = Matrix([[0, 9, 3, 0], [9, 8, 0, 8], [1, 8, 5, 3], [0, 0, 5, 8]])
    >>> m2 = Matrix([[0, 9, 1, 0], [9, 8, 8, 0], [3, 0, 5, 5], [0, 8, 3, 8]])
    >>> m1.transpose() == m2
    True
    >>> m1.transpose().transpose() == m1
    True

    >>> identity().transpose() == identity()
    True

    >>> Matrix([[1, 5], [-3, 2]]).determinant
    17

    >>> Matrix([[1, 5, 0], [-3, 2, 7], [0, 6, -3]]).submatrix(0, 2)
    Matrix([[-3, 2], [0, 6]])

    >>> Matrix([[-6, 1, 1, 6], [-8, 5, 8, 6], [-1, 0, 8, 2], [-7, 1, -1, 1]]).submatrix(2, 1)
    Matrix([[-6, 1, 6], [-8, 8, 6], [-7, -1, 1]])

    >>> Matrix([[3, 5, 0], [2, -1, -7], [6, -1, 5]]).minor(1, 0)
    25

    >>> m = Matrix([[3, 5, 0], [2, -1, -7], [6, -1, 5]])
    >>> m.cofactor(0, 0)
    -12
    >>> m.cofactor(1, 0)
    -25

    >>> Matrix([[1, 2, 6], [-5, 8, -4], [2, 6, 4]]).determinant
    -196

    >>> Matrix([[-2, -8, 3, 5], [-3, 1, 7, 3], [1, 2, -9, 6], [-6, 7, 7, -9]]).determinant
    -4071

    >>> m1 = Matrix([[3, -9, 7, 3], [3, -8, 2, -9], [-4, 4, 4, 1], [-6, 5, -1, 1]])
    >>> m2 = Matrix([[8, 2, 2, 2], [3, -1, 7, 0], [7, 0, 5, 4], [6, -2, 0, 5]])
    >>> m1 @ m2 @ m2.inverse() == m1
    True
    """

    def __init__(self, values):
        # type: (list[list[float]]) -> None
        """Initialize a matrix."""
        self.rows = values
        self.height = len(values)
        self.width = len(values[0])
        self._cols = None # type: list[list[float]]
        self._inverse = None # type: Optional[Matrix]

    @property
    def cols(self):
        # type: () -> list[list[float]]
        """Get the columns of the matrix."""
        if self._cols is None:
            self._cols = [
                [self.rows[r][c] for r in range(self.height)]
                for c in range(self.width)
            ]
        return self._cols

    @property
    def is_tuple(self):
        # type: () -> bool
        """Return True if the matrix is a 4-tuple."""
        return self.height == 1 and self.width == 4

    @property
    def is_vector(self):
        # type: () -> bool
        """Return True if the matrix is a graphics vector."""
        return self.is_tuple and self.rows[0][3] == 0

    @property
    def is_point(self):
        # type: () -> bool
        """Return True if the matrix is a graphics point."""
        return self.is_tuple and self.rows[0][3] == 1

    @property
    def x(self):
        # type: () -> float
        """Return the x value of a 4-tuple."""
        return self.rows[0][0]

    @property
    def y(self):
        # type: () -> float
        """Return the y value of a 4-tuple."""
        return self.rows[0][1]

    @property
    def z(self):
        # type: () -> float
        """Return the z value of a 4-tuple."""
        return self.rows[0][2]

    @property
    def w(self): # pylint: disable = invalid-name
        # type: () -> float
        """Return the w value of a 4-tuple."""
        return self.rows[0][3]

    @property
    def magnitude(self):
        # type: () -> float
        """Return the magnitude of a 4-tuple."""
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __eq__(self, other):
        # type: (Any) -> bool
        return (
            self.height == other.height and self.width == other.width
            and all(
                isclose(self_val, other_val, abs_tol=EPSILON)
                for self_row, other_row in zip(self.rows, other.rows)
                for self_val, other_val in zip(self_row, other_row)
            )
        )

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
            return f'Matrix({str(self.rows)})'

    def __add__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix([
            [val1 + val2 for val1, val2 in zip(row1, row2)]
            for row1, row2 in zip(self.rows, other.rows)
        ])

    def __sub__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix([
            [val1 - val2 for val1, val2 in zip(row1, row2)]
            for row1, row2 in zip(self.rows, other.rows)
        ])

    def __neg__(self):
        # type: () -> Matrix
        return Matrix([
            [-val for val in row]
            for row in self.rows
        ])

    def __mul__(self, other):
        # type: (Union[int,float]) -> Matrix
        result = []
        for row in self.rows:
            result.append([val * other for val in row])
        return Matrix(result)

    def __rmul__(self, other):
        # type: (Union[int,float]) -> Matrix
        return self * other

    def __truediv__(self, other):
        # type: (Union[int,float]) -> Matrix
        return self * (1 / other)

    def __matmul__(self, other):
        # type: (Matrix) -> Matrix
        is_tuple = False
        if other.is_tuple:
            other = other.transpose()
            is_tuple = True
        result = []
        for r in range(self.height):
            row = self.rows[r]
            result_row = []
            for c in range(other.width):
                col = other.cols[c]
                result_row.append(sum(a * b for a, b in zip(row, col)))
            result.append(result_row)
        if is_tuple:
            return Matrix(result).transpose()
        else:
            return Matrix(result)

    def normalize(self):
        # type: () -> Matrix
        """Normalize a graphics point/vector."""
        magnitude = self.magnitude
        return Vector3D(self.x / magnitude, self.y / magnitude, self.z / magnitude)

    def reflect(self, other):
        # type: (Matrix) -> Matrix
        """Reflect across another 4-tuple."""
        normal = other.normalize()
        return self - normal * 2 * self.dot(normal)

    def dot(self, other):
        # type: (Matrix) -> float
        """Take the dot product with another 4-tuple."""
        return (self @ other.transpose()).rows[0][0]

    def cross(self, other):
        # type: (Matrix) -> Matrix
        """Take the cross product with another matrix."""
        return Vector3D(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def transpose(self):
        # type: () -> Matrix
        """Transpose the matrix."""
        return Matrix(self.cols)

    @property
    def determinant(self):
        # type: () -> float
        """Calculate the determinant."""
        if self.height == 2 and self.width == 2:
            return self.rows[0][0] * self.rows[1][1] - self.rows[0][1] * self.rows[1][0]
        else:
            return sum(self.rows[0][i] * self.cofactor(0, i) for i in range(self.width))

    def submatrix(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> Matrix
        """Slice out a submatrix."""
        result = []
        for r, row in enumerate(self.rows):
            if r == dr:
                continue
            result.append(row[:dc] + row[dc + 1:])
        return Matrix(result)

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
            return -self.minor(dr, dc)

    @property
    def invertible(self):
        # type: () -> bool
        """Return True if the matrix is invertible."""
        return self.determinant != 0

    def inverse(self):
        # type: () -> Matrix
        """Inverse the matrix."""
        if self._inverse is None:
            result = []
            for r in range(self.height):
                result.append([self.cofactor(r, c) for c in range(self.width)])
            self._inverse = Matrix(result).transpose() / self.determinant
        return self._inverse

    def translate(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """Translate the matrix.

        >>> identity().translate(5, -3, 2) @ Point3D(-3, 4, 5) == Point3D(2, 1, 7)
        True

        >>> identity().translate(5, -3, 2).inverse() @ Point3D(-3, 4, 5) == Point3D(-8, 7, 3)
        True

        >>> identity().translate(5, -3, 2) @ Vector3D(-3, 4, 5) == Vector3D(-3, 4, 5)
        True
        """
        return (
            Matrix([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])
            @ self
        )

    def scale(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """Scale the matrix.

        >>> identity().scale(2, 3, 4) @ Point3D(-4, 6, 8) == Point3D(-8, 18, 32)
        True

        >>> identity().scale(2, 3, 4) @ Vector3D(-4, 6, 8) == Vector3D(-8, 18, 32)
        True

        >>> identity().scale(2, 3, 4).inverse() @ Point3D(-4, 6, 8) == Point3D(-2, 2, 2)
        True
        """
        return (
            Matrix([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_x(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the x-axis."""
        return (
            Matrix([[1, 0, 0, 0], [0, cos(r), -sin(r), 0], [0, sin(r), cos(r), 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_y(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the y-axis."""
        return (
            Matrix([[cos(r), 0, sin(r), 0], [0, 1, 0, 0], [-sin(r), 0, cos(r), 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_z(self, r):
        # type: (float) -> Matrix
        """Rotate the matrix along the z-axis."""
        return (
            Matrix([[cos(r), -sin(r), 0, 0], [sin(r), cos(r), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            @ self
        )

    def shear(self, x_y, x_z, y_x, y_z, z_x, z_y):
        # type: (float, float, float, float, float, float) -> Matrix
        """Shear the matrix.

        >>> identity().shear(1, 0, 0, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(5, 3, 4)
        True
        >>> identity().shear(0, 1, 0, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(6, 3, 4)
        True
        >>> identity().shear(0, 0, 1, 0, 0, 0) @ Point3D(2, 3, 4) == Point3D(2, 5, 4)
        True
        >>> identity().shear(0, 0, 0, 1, 0, 0) @ Point3D(2, 3, 4) == Point3D(2, 7, 4)
        True
        >>> identity().shear(0, 0, 0, 0, 1, 0) @ Point3D(2, 3, 4) == Point3D(2, 3, 6)
        True
        >>> identity().shear(0, 0, 0, 0, 0, 1) @ Point3D(2, 3, 4) == Point3D(2, 3, 7)
        True
        """
        return (
            Matrix([[1, x_y, x_z, 0], [y_x, 1, y_z, 0], [z_x, z_y, 1, 0], [0, 0, 0, 1]])
            @ self
        )


def Vector3D(x=0, y=0, z=0): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    """Create a 4-tuple that represents a 3D vector."""
    return Matrix([[x, y, z, 0]])


def Point3D(x=0, y=0, z=0): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    """Create a 4-tuple that represents a 3D point."""
    return Matrix([[x, y, z, 1]])


def identity():
    # type: () -> Matrix
    """Create an identity matrix.

    >>> identity() == Matrix([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
    True
    """
    return Matrix([(i * [0.0]) + [1.0] + (3 - i) * [0.0] for i in range(4)])
