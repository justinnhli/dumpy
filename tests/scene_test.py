"""Tests for scene.py."""

from dumpy.game_object import GameObject
from dumpy.polygon import Polygon
from dumpy.scene import HierarchicalHashGrid
from dumpy.simplex import Point2D


def test_hierarchical_hash_grid():
    # type: () -> None
    """Test HierarchicalHashGrid."""
    # initialize the HierarchicalHashGrid
    hhg = HierarchicalHashGrid()
    hhg.set_collision_group_pairs([('test', 'test')])
    # create and add the objects
    objects = []
    data = [
        (60, 110, 20, 5),
        (60, 120, 20, 5),
        (60, 70, 20, 5),
        (60, 170, 35, 6),
    ]
    for x, y, radius, _ in data:
        obj = GameObject()
        obj.points_matrix = Polygon.ellipse(radius, radius)
        obj.position = Point2D(x, y)
        obj.radius = radius
        obj.collision_groups.add('test')
        hhg.add(obj)
        objects.append(obj)
    # test that the objects are in the appropriate grid
    for obj, (*_, exponent) in zip(objects, data):
        grid = hhg.grids[exponent]
        assert grid
        grid_objects = []
        for coord in grid.populated_coords:
            for grid_object in grid.cells[coord]:
                grid_objects.append(grid_object)
        assert obj in grid_objects
    collisions = list(hhg.collisions)
    assert len(collisions) == 2
    colliding_objects = set()
    for obj1, obj2, _ in collisions:
        colliding_objects.add(obj1)
        colliding_objects.add(obj2)
    assert len(colliding_objects) == 2
    assert objects[0] in colliding_objects
    assert objects[1] in colliding_objects
