"""The Transform class."""

from functools import cached_property
from math import sin, cos, pi as PI
from typing import Any

from .matrix import Matrix, identity
from .root_class import RootClass


class Transform(RootClass):
    """A transform."""

    def __init__(self, x=0, y=0, theta=0, scale=1):
        # type: (float, float, float, float) -> None
        """Initialize the Transform."""
        super().__init__()
        self.x = x
        self.y = y
        self.theta = theta
        self.scale = scale

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.x, self.y, self.theta, self.scale

    @cached_property
    def radians(self):
        # type: () -> float
        """Return the rotation."""
        return self.theta * PI

    @cached_property
    def matrix(self):
        # type: () -> Matrix
        """Create the transformation matrix."""
        return (
            (self.scale * identity())
            .rotate_z(self.radians)
            .translate(self.x, self.y, 0)
        )

    @cached_property
    def inverse(self):
        # type: () -> Transform
        """Return the inverse transform.

        Equivalent to:

        return (
            Transform(scale=(1 / self.scale))
            @ Transform(theta=-self.theta)
            @ Transform(-self.x, -self.y)
        )
        """
        sin_radians = sin(self.radians)
        cos_radians = cos(self.radians)
        return Transform(
            (-self.x * cos_radians - self.y * sin_radians) / self.scale,
            (self.x * sin_radians - self.y * cos_radians) / self.scale,
            -self.theta,
            1 / self.scale,
        )

    def __round__(self, ndigits=0):
        # type: (int) -> Transform
        """Round the transform."""
        return Transform(
            round(self.x, ndigits),
            round(self.y, ndigits),
            round(self.theta, ndigits),
            round(self.scale, ndigits),
        )

    def __matmul__(self, other):
        # type: (Any) -> Any
        """Matrix multiplication.

        Returning NotImplemented allows other classes to implement __rmatmul__.
        """
        if isinstance(other, Transform):
            # from https://gamedev.stackexchange.com/a/207764
            return Transform(
                self.x + self.scale * (other.x * cos(self.radians) - other.y * sin(self.radians)),
                self.y + self.scale * (other.x * sin(self.radians) + other.y * cos(self.radians)),
                other.theta + self.theta,
                other.scale * self.scale,
            )
        else:
            return NotImplemented

    def calculate_hash(self):
        # type: () -> int
        return hash((self.x, self.y, self.theta, self.scale))
