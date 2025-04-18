"""A scene of objects."""

from collections import defaultdict
from functools import cached_property
from itertools import product
from math import ceil, log2
from typing import Iterator, Iterable

from .simplex import Point2D, Vector2D
from .camera import Camera
from .game_object import GameObject


class HashGrid:
    """A hash grid."""

    HALF_OFFSETS = [
        Vector2D(-1, -1),
        Vector2D(-1, 0),
        Vector2D(-1, 1),
        Vector2D(0, -1),
    ]
    FULL_OFFSETS = [
        *HALF_OFFSETS,
        Vector2D(0, 0),
        Vector2D(0, 1),
        Vector2D(1, -1),
        Vector2D(1, 0),
        Vector2D(1, 1),
    ]

    def __init__(self, grid_size):
        # type: (int) -> None
        self.grid_size = grid_size
        self.num_objects = 0
        self.cells = defaultdict(list) # type: dict[Point2D, list[GameObject]]
        self.populated_coords = set() # type: set[Point2D]

    def __len__(self):
        # type: () -> int
        return self.num_objects

    @property
    def objects(self):
        # type: () -> Iterator[GameObject]
        """Get all objects in the grid."""
        for cell in self.cells.values():
            yield from cell

    def to_cell_coord(self, game_object):
        # type: (GameObject) -> Point2D
        """Calculate the cell for an object."""
        return game_object.position // self.grid_size

    def add(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the grid."""
        coord = self.to_cell_coord(game_object)
        self.cells[coord].append(game_object)
        self.num_objects += 1
        self.populated_coords.add(coord)

    def remove(self, game_object):
        # type: (GameObject) -> None
        """Remove an object to the grid."""
        coord = self.to_cell_coord(game_object)
        self.cells[coord].remove(game_object)
        self.num_objects -= 1
        if not self.cells[coord]:
            self.populated_coords.remove(coord)

    def get_collisions(self):
        # type: () -> Iterator[tuple[GameObject, GameObject]]
        """Get all collisions."""
        for coord in self.populated_coords:
            cell = self.cells[coord]
            for i, obj1 in enumerate(cell):
                # find collisions in the current cell
                for obj2 in cell[i + 1:]:
                    if obj1.is_colliding(obj2):
                        yield (obj1, obj2)
                # find collisions in the adjacent cells
                yield from self.get_collisions_with(obj1, half_neighbors=True)

    def get_collisions_with(self, game_object, half_neighbors=False):
        # type: (GameObject, bool) -> Iterator[tuple[GameObject, GameObject]]
        """Get collisions with an object."""
        coord = self.to_cell_coord(game_object)
        if half_neighbors:
            offsets = HashGrid.HALF_OFFSETS
        else:
            offsets = HashGrid.FULL_OFFSETS
        for offset in offsets:
            neighbor_coord = coord + offset
            if neighbor_coord not in self.cells:
                continue
            for obj2 in self.cells[neighbor_coord]:
                if game_object != obj2 and game_object.is_colliding(obj2):
                    yield (game_object, obj2)


class HierarchicalHashGrid:
    """A hierarchical hash grid."""

    def __init__(self, min_exponent=4, max_exponent=None):
        # type: (int, int) -> None
        """Initialize a hierarchical hash grid."""
        if max_exponent is None:
            max_exponent = min_exponent + 10
        self.min_exponent = min_exponent
        self.max_exponent = max_exponent
        self.num_objects = 0
        self.grids = [] # type: list[HashGrid]
        for exponent in range(min_exponent):
            self.grids.append(None)
        for exponent in range(min_exponent, max_exponent + 1):
            self.grids.append(HashGrid(2 ** exponent))
        self.objects = [] # type: list[GameObject]
        self.collision_group_pairs = set() # type: set[tuple[str, str]]

    @cached_property
    def exponent_grids(self):
        # type: () -> list[tuple[int, HashGrid]]
        return list(zip(
            range(self.min_exponent, self.max_exponent + 1),
            self.grids[self.min_exponent:],
        ))

    @property
    def all_collisions(self):
        # type: () -> Iterator[tuple[GameObject, GameObject]]
        """Yield all collisions."""
        for exponent, small_grid in self.exponent_grids:
            yield from small_grid.get_collisions()
            for game_object in small_grid.objects:
                for large_grid in self.grids[exponent + 1:]:
                    yield from large_grid.get_collisions_with(game_object)

    @property
    def collisions(self):
        # type: () -> Iterator[tuple[GameObject, GameObject, tuple[str, str]]]
        """Yield all collisions of registered group pairs."""
        for obj1, obj2 in self.all_collisions:
            for group1, group2 in product(obj1.collision_groups, obj2.collision_groups):
                key = (group1, group2)
                if key in self.collision_group_pairs:
                    yield obj1, obj2, key
                key = (group2, group1)
                if key in self.collision_group_pairs:
                    yield obj2, obj1, key

    def add(self, game_object):
        # type: (GameObject) -> None
        """Add an object to the grid."""
        self.objects.append(game_object)
        exponent = min(
            max(ceil(log2(game_object.radius)), self.min_exponent),
            self.max_exponent,
        )
        self.grids[exponent].add(game_object)
        self.num_objects += 1

    def get_in_view(self, camera):
        # type: (Camera) -> list[GameObject]
        """Get all objects in view of the camera."""
        return self.objects # FIXME

    def set_collision_group_pairs(self, collision_pairs):
        # type: (Iterable[tuple[str, str]]) -> None
        """Set collision group pairs to detect."""
        for group_pair in collision_pairs:
            self.collision_group_pairs.add(group_pair)
