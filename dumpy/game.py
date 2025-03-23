"""The abstract Game class."""

from time import monotonic_ns as get_nsec_time
from typing import Callable

from .camera import Camera
from .canvas import Canvas, Input, EventCallback
from .game_object import GameObject
from .scene import Scene


class Game:
    """A game."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        """Initialize the Game."""
        # components
        self.scene = Scene()
        self.canvas = Canvas(width, height)
        self.camera = Camera(self.canvas)
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
        # type: (str, str, Callable[[GameObject, GameObject], None]) -> None
        """Add a collision handler."""
        pass # FIXME

    def dispatch_tick(self):
        # type: () -> None
        """Deal with time passing."""
        # calculate elapsed time since last tick
        curr_time = Game.get_time()
        if self.prev_time is None:
            elapsed_time = 0
        else:
            elapsed_time = curr_time - self.prev_time
        # FIXME update all physics objects
        # draw all objects
        for game_object in self.scene.get_in_view(self.camera):
            self.camera.draw_points_matrix(
                game_object.points_matrix,
                fill_color=game_object.fill_color,
                line_color=game_object.line_color,
            )
        # update timer
        self.prev_time = curr_time

    def start(self):
        # type: () -> None
        """Start the game."""
        for input_event, callback in self.keybinds.items():
            self.canvas.bind(input_event, callback)
        self.prev_time = Game.get_time()
        self.canvas.start(self.dispatch_tick, 40)

    @staticmethod
    def get_time():
        # type: () -> int
        """Return a millisecond-level time."""
        return get_nsec_time() // 1000
