#!/home/justinnhli/.local/share/venv/dumpy/bin/python3

import sys
from random import Random
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dumpy.game import Game
from dumpy.game_object import GameObject, PhysicsObject
from dumpy.polygon import Polygon
from dumpy.simplex import Point2D, Vector2D


class Ball(PhysicsObject):
    """A bouncy ball."""

    ELLIPSE = Polygon.ellipse(15, 15)

    def __init__(self):
        # type: () -> None
        super().__init__()
        self.geometry = Ball.ELLIPSE
        self.radius = 15

    def bounce_vertical(self, _):
        # type: (GameObject) -> None
        """Bounce the ball vertically."""
        self.velocity = Vector2D.from_matrix(self.velocity.matrix.y_reflection)

    def bounce_horizontal(self, _):
        # type: (GameObject) -> None
        """Bounce the ball horizontally."""
        self.velocity = Vector2D.from_matrix(self.velocity.matrix.x_reflection)


class Wall(GameObject):
    """A boundary wall."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        super().__init__()
        self.width = width
        self.height = height
        self.geometry = Polygon.rectangle(width, height)
        self.radius = max(width, height) / 2


class Bouncy(Game):
    """A bouncing ball collision demonstration."""

    def __init__(self, num_balls):
        # type: (int) -> None
        super().__init__(600, 400)
        self.rng = Random(8675309)
        self.num_balls = num_balls
        self.create_objects()
        self.register_collisions()

    def create_objects(self):
        # type: () -> None
        """Create the objects."""
        # add walls
        wall_thickness = 50
        window_width = self.window_width - (wall_thickness // 2)
        window_height = self.window_height - (wall_thickness // 2)
        top_wall = Wall(window_width + 2 * wall_thickness, wall_thickness)
        top_wall.add_to_collision_group('h_walls')
        top_wall.move_to(Point2D(0, (window_height + wall_thickness) // 2))
        self.add_object(top_wall)
        bottom_wall = Wall(window_width + 2 * wall_thickness, wall_thickness)
        bottom_wall.add_to_collision_group('h_walls')
        bottom_wall.move_to(Point2D(0, -(window_height + wall_thickness) // 2))
        self.add_object(bottom_wall)
        left_wall = Wall(wall_thickness, window_height)
        left_wall.add_to_collision_group('v_walls')
        left_wall.move_to(Point2D(-(window_width + wall_thickness) // 2, 0))
        self.add_object(left_wall)
        right_wall = Wall(wall_thickness, window_height)
        right_wall.add_to_collision_group('v_walls')
        right_wall.move_to(Point2D((window_width + wall_thickness) // 2, 0))
        self.add_object(right_wall)
        # add the balls
        for _ in range(self.num_balls):
            ball = Ball()
            ball.add_to_collision_group('balls')
            ball.move_to(Point2D(
                self.rng.randrange(
                    -(window_width // 2),
                    (window_width // 2) + 1,
                ),
                self.rng.randrange(
                    -(window_height // 2),
                    (window_height // 2) + 1,
                ),
            ))
            ball.velocity = Vector2D(
                self.rng.randrange(-5, 6),
                self.rng.randrange(-5, 6),
            )
            self.add_object(ball)

    def register_collisions(self):
        # type: () -> None
        """Register the collision callbacks."""
        # add collision detection
        self.on_collision('balls', 'h_walls', Ball.bounce_vertical)
        self.on_collision('balls', 'v_walls', Ball.bounce_horizontal)


def main():
    # type: () -> None
    """Provide a CLI entry point."""
    Bouncy(20).start()


if __name__ == '__main__':
    main()
