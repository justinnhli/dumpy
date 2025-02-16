"""The Transform class."""

from functools import cached_property
from math import pi as PI
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
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the components of this object."""
        return self.x, self.y, self.theta, self.scale

    def __add__(self, other):
        # type: (Transform) -> Transform
        assert isinstance(other, type(self))
        return Transform(
            self.x + other.x,
            self.y + other.y,
            self.theta + other.theta,
            self.scale * other.scale,
        )

    def __neg__(self):
        # type: () -> Transform
        return Transform(-self.x, -self.y, -self.theta, 1 / self.scale)

    def calculate_hash(self):
        # type: () -> int
        return hash((self.x, self.y, self.theta, self.scale))
