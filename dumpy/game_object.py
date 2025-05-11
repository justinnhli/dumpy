"""GameObject and its hierarchy."""

from math import pi as PI

from .color import Color
from .simplex import PointsMatrix, Point2D, Vector2D
from .transform import Transform
from .metaprogramming import cached_property


class GameObject:
    """A basic game object."""

    def __init__(self): # pylint: disable = unused-argument
        # type: () -> None
        """Initialize the GameObject."""
        self.points_matrix = None # type: PointsMatrix
        self.radius = 0 # type: float
        self.line_color = None # type: Color
        self.fill_color = None # type: Color
        self._position = Point2D()
        self._theta = 0 # type: float
        self.collision_groups = set() # type: set[str]

    def __hash__(self):
        # type: () -> int
        return id(self)

    def __repr__(self):
        # type: () -> str
        return f'{type(self).__name__}({self.position})'

    @property
    def position(self):
        # type: () -> Point2D
        """Return the position."""
        return self._position

    @property
    def theta(self):
        # type: () -> float
        """Return the rotation in 2pi radians."""
        return self._theta

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

    @cached_property('transform', 'points_matrix')
    def transformed_points_matrix(self):
        # type: () -> PointsMatrix
        """The transformed PointsMatrix."""
        return self.transform @ self.points_matrix

    def move_to(self, point):
        # type: (Point2D) -> None
        """Move the object to the point."""
        self._position = point

    def move_by(self, vector):
        # type: (Vector2D) -> None
        """Move the object by the vector."""
        self._position += vector

    def rotate_to(self, theta):
        # type: (float) -> None
        """Rotate the object to the angle."""
        self._theta = theta

    def rotate_by(self, theta):
        # type: (float) -> None
        """Rotate the object by the angle."""
        self._theta += theta

    def update(self):
        # type: () -> None
        """Update the object."""
        pass

    def squared_distance(self, other):
        # type: (GameObject) -> float
        """Calculate the squared distance to another object."""
        return self.position.squared_distance(other.position)

    def is_colliding(self, other):
        # type: (GameObject) -> bool
        """Determine if two objects are colliding.

        This uses the hyperplane separation/separating axis theorem, which
        states that if two convex objects are disjoint, there must be a line
        onto which the objects' projections are disjoint. Since the theorem
        only applies to convex objects, this implementation compares all pairs
        of triangles between the two polygons; if all pairs of triangles are
        separable, the polygons must also be disjoint.

        Additionally, the vector between the two centroids is tried first as a
        potential shortcut.
        """
        # try the vector between centroids first
        points_matrix1 = self.transformed_points_matrix
        points_matrix2 = other.transformed_points_matrix
        vector = points_matrix1.centroid - points_matrix2.centroid
        if GameObject.separated_on_axis(points_matrix1, points_matrix2, vector):
            return False
        # revert to the standard approach of trying all segment normals
        checked = set() # type: set[Vector2D]
        for points_matrix in (points_matrix1, points_matrix2):
            for segment in points_matrix.segments:
                normal = segment.normal
                if normal in checked:
                    continue
                checked.add(normal)
                if GameObject.separated_on_axis(points_matrix1, points_matrix2, normal):
                    return False
        return True

    @staticmethod
    def separated_on_axis(points_matrix1, points_matrix2, vector):
        # type: (PointsMatrix, PointsMatrix, Vector2D) -> bool
        """Check if an axis separates two points matrices.

        This function does not use Triangle.is_colliding() to take advantage of caching.
        """
        denominator = (vector.x * vector.x + vector.y * vector.y) ** (1/2)
        cache = {}
        for convex1 in points_matrix1.triangles:
            projected1 = []
            for point in convex1.points:
                if point not in cache:
                    cache[point] = (vector.x * point.x + vector.y * point.y) / denominator
                projected1.append(cache[point])
            min1 = min(projected1)
            max1 = max(projected1)
            for convex2 in points_matrix2.triangles:
                projected2 = []
                for point in convex2.points:
                    if point not in cache:
                        cache[point] = (vector.x * point.x + vector.y * point.y) / denominator
                    projected2.append(cache[point])
                min2 = min(projected2)
                max2 = max(projected2)
                if min1 <= max2 and min2 <= max1:
                    return False
        return True


class PhysicsObject(GameObject):
    """A game object with kinematics."""

    def __init__(self):
        # type: () -> None
        """Initialize the PhysicsObject."""
        super().__init__()
        self.velocity = Vector2D()
        self.angular_velocity = 0
        self.acceleration = Vector2D()
        self.angular_acceleration = 0

    def update(self):
        # type: () -> None
        """Update the velocity and the position."""
        self.velocity += self.acceleration
        self.angular_velocity += self.angular_acceleration
        self.move_by(self.velocity)
        self.rotate_by(self.angular_velocity)
