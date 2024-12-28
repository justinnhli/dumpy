"""Mix-in classes."""

from typing import Any

from .matrix import Matrix, Point2D


class TransformMixIn:
    """MixIn for transform information."""

    def __init__(self, *args, position=None, rotation=0, **kwargs):
        # type: (Any, Matrix, float, Any) -> None
        """Initialize position and rotation."""
        # pylint: disable = unused-argument
        if position is None:
            position = Point2D(0, 0)
        self.position = position
        self.rotation = rotation
