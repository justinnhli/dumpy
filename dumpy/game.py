"""The abstract Game class."""

from time import monotonic_ns as get_nsec_time
from tkinter import Event
from typing import Callable

from .camera import Camera
from .canvas import Canvas
from .game_object import GameObject
from .scene import Scene


class Game:
    """A game."""

    def __init__(self, width, height):
        # type: (int, int) -> None
        # components
        self.scene = Scene()
        self.canvas = Canvas(width, height)
        self.camera = Camera(self.canvas)
        # settings
        self.keybinds = {} # type: dict[str, Callable[[str], None]]
        # state
        self.prev_time = None # type: int

    def add_object(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the scene."""
        self.scene.add(game_object)

    def bind_key(self, key, callback):
        # type: (str, Callable[[str], None]) -> None
        """Add a keybind."""
        self.keybinds[key] = callback

    def on_collision(self, group1, group2, callback):
        # type: (str, str, Callable[[GameObject, GameObject], None]) -> None
        """Add a collision handler."""
        pass # FIXME

    def dispatch_tick(self):
        # type: () -> None
        """Deal with time passing."""
        # calculate elapsed time since last tick
        curr_time = Game.get_time()
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

    def dispatch_input(self, event):
        # type: (Event) -> None
        """Deal with input."""
        self.keybinds[f'<{event.keysym}>'](event.keysym)

    def start(self):
        # type: () -> None
        """Start the game."""
        for key in self.keybinds:
            self.canvas.bind_key(key, self.dispatch_input)
        self.prev_time = Game.get_time()
        self.canvas.start(self.dispatch_tick, 40)

    @staticmethod
    def get_time():
        # type: () -> int
        """Return a millisecond-level time."""
        return get_nsec_time() // 1000
