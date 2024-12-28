"""Mix-in classes."""

from functools import cached_property
from typing import Any

from .matrix import Matrix, Vector2D, identity


class Transform:
    """A transform."""

    def __init__(self, translation=None, rotation=0):
        # type: (Matrix, float) -> None
        """Initialize the Transform."""
        if translation is None:
            translation = Vector2D()
        self.translation = translation
        self.rotation = rotation

    @cached_property
    def x(self):
        # type: () -> float
        """Return the x value of the translation."""
        return self.translation.x

    @cached_property
    def y(self):
        # type: () -> float
        """Return the y value of the translation."""
        return self.translation.y

    @cached_property
    def theta(self):
        # type: () -> float
        """Return the rotation."""
        return self.rotation

    @cached_property
    def matrix(self):
        # type: () -> Matrix
        """Create the transformation matrix."""
        return (
            identity()
            .rotate_z(self.rotation)
            .translate(self.translation.x, self.translation.y, 0)
        )

    def __add__(self, other):
        # type: (Transform) -> Transform
        return Transform(
            Vector2D(self.x + other.x, self.y + other.y),
            self.rotation + other.rotation,
        )

    def __neg__(self):
        # type: () -> Transform
        return Transform(-self.translation, -self.rotation)


class TransformMixIn:
    """MixIn for objects with translation and rotation."""

    def __init__(self, *args, translation=None, rotation=0, **kwargs):
        # type: (Any, Matrix, float, Any) -> None
        """Initialize the Transform."""
        # pylint: disable = unused-argument
        self.transform = Transform(translation, rotation)

    def move(self, transform):
        # type: (Transform) -> None
        """Compose the transforms."""
        self.transform += transform

    def move_to(self, transform):
        # type: (Transform) -> None
        """Replace the transform."""
        self.transform = transform
