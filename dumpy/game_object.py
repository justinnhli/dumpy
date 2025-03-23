"""GameObject and its hierarchy."""

from math import pi as PI

from .color import Color
from .simplex import PointsMatrix, Point2D, Vector2D
from .transform import Transform


class GameObject:
    """A basic game object."""

    def __init__(self): # pylint: disable = unused-argument
        # type: () -> None
        self.points_matrix = None # type: PointsMatrix
        self.line_color = Color.from_hex('#000000')
        self.fill_color = None
        self.position = Point2D()
        self.theta = 0 # type: float

    @property
    def radians(self):
        # type: () -> float
        """Return the rotation in radians."""
        return self.theta * PI

    @property
    def transform(self):
        # type: () -> Transform
        """The transform defined by the position of this object."""
        return Transform(self.position.x, self.position.y, self.theta)

    def move_to(self, x, y):
        # type: (float, float) -> None
        """Move the object to the point."""
        self.position = Point2D(x, y)

    def move_by(self, x, y):
        # type: (float, float) -> None
        """Move the object by the vector."""
        self.position += Vector2D(x, y)

    def rotate_to(self, theta):
        # type: (float) -> None
        """Rotate the object to the angle."""
        self.theta = theta

    def rotate_by(self, theta):
        # type: (float) -> None
        """Rotate the object by the angle."""
        self.theta += theta

    def update(self):
        # type: () -> None
        """Update the object."""
        pass


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
        self.theta += self.angular_velocity
