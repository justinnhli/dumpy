"""GameObject and its hierarchy."""

from .polygon import Polygon
from .simplex import Point2D, Vector2D
from .transform import Transform


class GameObject:
    """A basic game object."""

    def __init__(self): # pylint: disable = unused-argument
        # type: () -> None
        self.polygon = None # type: Polygon
        self.position = Point2D()
        self.rotation = 0 # type: float

    @property
    def transform(self):
        # type: () -> Transform
        """The transform defined by the position of this object."""
        return Transform(self.position.x, self.position.y, self.rotation)

    def update(self):
        # type: () -> None
        """Update the object."""


class PhysicsObject(GameObject):
    """A game object with kinematics."""

    def __init__(self):
        # type: () -> None
        super().__init__()
        self.velocity = Vector2D()
        self.angular_velocity = 0
        self.acceleration = Vector2D()
        self.angular_acceleration = 0

    def update(self):
        # type: () -> None
        self.velocity += self.acceleration
        self.angular_velocity += self.angular_acceleration
        self.position += self.velocity
        self.rotation += self.angular_velocity
