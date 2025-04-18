"""The abstract Game class."""

from time import monotonic_ns as get_nsec_time
from typing import Callable

from .camera import Camera
from .canvas import Canvas, Input, EventCallback
from .game_object import GameObject
from .scene import HierarchicalHashGrid


CollisionCallback = Callable[[GameObject, GameObject], None]


class Game:
    """A game."""

    def __init__(self, window_width, window_height):
        # type: (int, int) -> None
        """Initialize the Game."""
        self.window_width = window_width
        self.window_height = window_height
        # components
        self.canvas = Canvas(window_width, window_height)
        self.camera = Camera(self.canvas)
        # objects
        self.scene = HierarchicalHashGrid()
        self.collision_callbacks = {} # type: dict[tuple[str, str], CollisionCallback]
        # settings
        self.keybinds = {} # type: dict[Input, EventCallback]
        # state
        self.prev_time = None # type: int

    def add_object(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the scene."""
        self.scene.add(game_object)

    def bind(self, input_event, callback):
        # type: (Input, EventCallback) -> None
        """Add a keybind."""
        self.keybinds[input_event] = callback

    def on_collision(self, group1, group2, callback):
        # type: (str, str, CollisionCallback) -> None
        """Add a collision handler."""
        self.collision_callbacks[(group1, group2)] = callback

    def dispatch_tick(self):
        # type: () -> None
        """Deal with time passing."""
        # calculate elapsed time since last tick
        curr_time = Game.get_time()
        if self.prev_time is None:
            elapsed_time = 0
        else:
            elapsed_time = curr_time - self.prev_time
        # update all physics objects
        # FIXME this should be integrated into collision detection, since only objects that move could have new collisions
        for obj in self.scene.objects:
            obj.update()
        # deal with collisions
        for obj1, obj2, group_pair in self.scene.collisions:
            self.collision_callbacks[group_pair](obj1, obj2)
        # draw all objects
        for game_object in self.scene.get_in_view(self.camera):
            self.camera.draw_points_matrix(
                game_object.transform @ game_object.points_matrix,
                fill_color=game_object.fill_color,
                line_color=game_object.line_color,
            )
        # update timer
        self.prev_time = curr_time

    def start(self):
        # type: () -> None
        """Start the game."""
        self.scene.set_collision_group_pairs(self.collision_callbacks.keys())
        for input_event, callback in self.keybinds.items():
            self.canvas.bind(input_event, callback)
        self.prev_time = Game.get_time()
        self.canvas.start(self.dispatch_tick, 40)

    @staticmethod
    def get_time():
        # type: () -> int
        """Return a millisecond-level time."""
        return get_nsec_time() // 1000
