#!/usr/bin/env python3

# pylint: disable = too-many-lines

from math import sqrt, isclose, sin, cos
from typing import Any, Optional, Union


EPSILON = 0.00001


class Matrix: # pylint: disable = too-many-public-methods
    """A matrix.

    >>> Point(3, -2, 5) + Vector(-2, 3, 1)
    Point(1, 1, 6)

    >>> Point(3, 2, 1) - Point(5, 6, 7)
    Vector(-2, -4, -6)

    >>> Point(3, 2, 1) - Vector(5, 6, 7)
    Point(-2, -4, -6)

    >>> Vector(3, 2, 1) - Vector(5, 6, 7)
    Vector(-2, -4, -6)

    >>> Tuple4(1, -2, 3, -4) * 3.5
    Tuple4(3.5, -7.0, 10.5, -14.0)

    >>> 0.5 * Tuple4(1, -2, 3, -4)
    Tuple4(0.5, -1.0, 1.5, -2.0)

    >>> Tuple4(1, -2, 3, -4) / 2
    Tuple4(0.5, -1.0, 1.5, -2.0)

    >>> Vector(1, 0, 0).magnitude
    1.0

    >>> Vector(0, 1, 0).magnitude
    1.0

    >>> Vector(0, 0, 1).magnitude
    1.0

    >>> Vector(1, 2, 3).magnitude == sqrt(14)
    True

    >>> Vector(-1, -2, -3).magnitude == sqrt(14)
    True

    >>> Vector(4, 0, 0).normalize()
    Vector(1.0, 0.0, 0.0)

    >>> Vector(1, 2, 3).normalize().magnitude
    1.0

    >>> Vector(1, 2, 3).dot(Vector(2, 3, 4))
    20

    >>> Vector(1, 2, 3).cross(Vector(2, 3, 4))
    Vector(-1, 2, -1)

    >>> Vector(2, 3, 4).cross(Vector(1, 2, 3))
    Vector(1, -2, 1)

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
    >>> t = Tuple4(1, 2, 3, 1)
    >>> m1 @ t
    Point(18, 24, 33)

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
        self.vals = values
        self.height = len(values)
        self.width = len(values[0])
        self._cols = None # type: list[list[float]]
        self._inverse = None # type: Optional[Matrix]

    @property
    def cols(self):
        # type: () -> list[list[float]]
        if self._cols is None:
            self._cols = [
                [self.rows[r][c] for r in range(self.height)]
                for c in range(self.width)
            ]
        return self._cols

    @property
    def is_tuple(self):
        # type: () -> bool
        return self.height == 1 and self.width == 4

    @property
    def is_vector(self):
        # type: () -> bool
        return self.is_tuple and self.vals[0][3] == 0

    @property
    def is_point(self):
        # type: () -> bool
        return self.is_tuple and self.vals[0][3] == 1

    @property
    def x(self):
        # type: () -> float
        return self.vals[0][0]

    @property
    def y(self):
        # type: () -> float
        return self.vals[0][1]

    @property
    def z(self):
        # type: () -> float
        return self.vals[0][2]

    @property
    def w(self): # pylint: disable = invalid-name
        # type: () -> float
        return self.vals[0][3]

    @property
    def magnitude(self):
        # type: () -> float
        return sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def __eq__(self, other):
        # type: (Any) -> bool
        return (
            self.height == other.height and self.width == other.width
            and all(
                isclose(self_val, other_val, abs_tol=EPSILON)
                for self_row, other_row in zip(self.vals, other.vals)
                for self_val, other_val in zip(self_row, other_row)
            )
        )

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        if self.is_tuple:
            vals = (
                str(abs(self.x) if self.x == 0 else self.x),
                str(abs(self.y) if self.y == 0 else self.y),
                str(abs(self.z) if self.z == 0 else self.z),
                str(abs(self.w) if self.w == 0 else self.w),
            )
            if self.is_vector:
                return f'Vector({", ".join(vals[:-1])})'
            elif self.is_point:
                return f'Point({", ".join(vals[:-1])})'
            else:
                return f'Tuple4({", ".join(vals)})'
        else:
            return f'Matrix({str(self.vals)})'

    def __add__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix([
            [val1 + val2 for val1, val2 in zip(row1, row2)]
            for row1, row2 in zip(self.vals, other.vals)
        ])

    def __sub__(self, other):
        # type: (Matrix) -> Matrix
        return Matrix([
            [val1 - val2 for val1, val2 in zip(row1, row2)]
            for row1, row2 in zip(self.vals, other.vals)
        ])

    def __neg__(self):
        # type: () -> Matrix
        return Matrix([
            [-val for val in row]
            for row in self.vals
        ])

    def __mul__(self, other):
        # type: (Union[int,float]) -> Matrix
        result = []
        for row in self.vals:
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
            row = self.vals[r]
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
        magnitude = self.magnitude
        return Vector(self.x / magnitude, self.y / magnitude, self.z / magnitude)

    def reflect(self, other):
        # type: (Matrix) -> Matrix
        normal = other.normalize()
        return self - normal * 2 * self.dot(normal)

    def dot(self, other):
        # type: (Matrix) -> float
        return (self @ other.transpose()).vals[0][0]

    def cross(self, other):
        # type: (Matrix) -> Matrix
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def transpose(self):
        # type: () -> Matrix
        return Matrix(self.cols)

    @property
    def determinant(self):
        # type: () -> float
        if self.height == 2 and self.width == 2:
            return self.vals[0][0] * self.vals[1][1] - self.vals[0][1] * self.vals[1][0]
        else:
            return sum(self.vals[0][i] * self.cofactor(0, i) for i in range(self.width))

    def submatrix(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> Matrix
        result = []
        for r, row in enumerate(self.vals):
            if r == dr:
                continue
            result.append(row[:dc] + row[dc + 1:])
        return Matrix(result)

    def minor(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> float
        return self.submatrix(dr, dc).determinant

    def cofactor(self, dr, dc): # pylint: disable = invalid-name
        # type: (int, int) -> float
        if (dr + dc) % 2 == 0:
            return self.minor(dr, dc)
        else:
            return -self.minor(dr, dc)

    @property
    def invertible(self):
        # type: () -> bool
        return self.determinant != 0

    def inverse(self):
        # type: () -> Matrix
        if self._inverse is None:
            result = []
            for r in range(self.height):
                result.append([self.cofactor(r, c) for c in range(self.width)])
            self._inverse = Matrix(result).transpose() / self.determinant
        return self._inverse

    def translate(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """
        >>> identity().translate(5, -3, 2) @ Point(-3, 4, 5)
        Point(2.0, 1.0, 7.0)

        >>> identity().translate(5, -3, 2).inverse() @ Point(-3, 4, 5)
        Point(-8.0, 7.0, 3.0)

        >>> identity().translate(5, -3, 2) @ Vector(-3, 4, 5)
        Vector(-3.0, 4.0, 5.0)
        """
        return (
            Matrix([[1, 0, 0, x], [0, 1, 0, y], [0, 0, 1, z], [0, 0, 0, 1]])
            @ self
        )

    def scale(self, x, y, z):
        # type: (float, float, float) -> Matrix
        """
        >>> identity().scale(2, 3, 4) @ Point(-4, 6, 8)
        Point(-8.0, 18.0, 32.0)

        >>> identity().scale(2, 3, 4) @ Vector(-4, 6, 8)
        Vector(-8.0, 18.0, 32.0)

        >>> identity().scale(2, 3, 4).inverse() @ Point(-4, 6, 8)
        Point(-2.0, 2.0, 2.0)
        """
        return (
            Matrix([[x, 0, 0, 0], [0, y, 0, 0], [0, 0, z, 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_x(self, r):
        # type: (float) -> Matrix
        return (
            Matrix([[1, 0, 0, 0], [0, cos(r), -sin(r), 0], [0, sin(r), cos(r), 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_y(self, r):
        # type: (float) -> Matrix
        return (
            Matrix([[cos(r), 0, sin(r), 0], [0, 1, 0, 0], [-sin(r), 0, cos(r), 0], [0, 0, 0, 1]])
            @ self
        )

    def rotate_z(self, r):
        # type: (float) -> Matrix
        return (
            Matrix([[cos(r), -sin(r), 0, 0], [sin(r), cos(r), 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
            @ self
        )

    def shear(self, x_y, x_z, y_x, y_z, z_x, z_y):
        # type: (float, float, float, float, float, float) -> Matrix
        """
        >>> identity().shear(1, 0, 0, 0, 0, 0) @ Point(2, 3, 4)
        Point(5.0, 3.0, 4.0)
        >>> identity().shear(0, 1, 0, 0, 0, 0) @ Point(2, 3, 4)
        Point(6.0, 3.0, 4.0)
        >>> identity().shear(0, 0, 1, 0, 0, 0) @ Point(2, 3, 4)
        Point(2.0, 5.0, 4.0)
        >>> identity().shear(0, 0, 0, 1, 0, 0) @ Point(2, 3, 4)
        Point(2.0, 7.0, 4.0)
        >>> identity().shear(0, 0, 0, 0, 1, 0) @ Point(2, 3, 4)
        Point(2.0, 3.0, 6.0)
        >>> identity().shear(0, 0, 0, 0, 0, 1) @ Point(2, 3, 4)
        Point(2.0, 3.0, 7.0)
        """
        return (
            Matrix([[1, x_y, x_z, 0], [y_x, 1, y_z, 0], [z_x, z_y, 1, 0], [0, 0, 0, 1]])
            @ self
        )


def Tuple4(x, y, z, w): # pylint: disable = invalid-name
    # type: (float, float, float, float) -> Matrix
    return Matrix([[x, y, z, w]])


def Vector(x, y, z): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    return Matrix([[x, y, z, 0]])


def Point(x, y, z): # pylint: disable = invalid-name
    # type: (float, float, float) -> Matrix
    return Matrix([[x, y, z, 1]])


def identity():
    # type: () -> Matrix
    """
    >>> identity()
    Matrix([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    """
    return Matrix([(i * [0.0]) + [1.0] + (3 - i) * [0.0] for i in range(4)])
