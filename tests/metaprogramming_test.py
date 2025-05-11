"""Tests for metaprogramming.py."""
# pylint: disable = comparison-with-callable, too-few-public-methods

from typing import NamedTuple

from dumpy.metaprogramming import cached_class, cached_property

class _CachedClassDummy(NamedTuple):
    x: int


@cached_class
class CachedClassDummy(_CachedClassDummy):
    """A dummy class to test cached_class."""

    def __new__(cls, x):
        return super(CachedClassDummy, cls).__new__(cls, x)

    def __init__(self, x): # pylint: disable = unused-argument
        # type: (int) -> None
        self.num_calls = 0

    @cached_property('x')
    def prop(self):
        # type: () -> str
        """Test property."""
        self.num_calls += 1
        return f'prop {self.x}'


def test_cached_class():
    # type: () -> None
    """Test cached_class."""
    x = CachedClassDummy(0)
    y = CachedClassDummy(0)
    z = CachedClassDummy(1)
    w = CachedClassDummy(2)
    assert x is y
    assert x is not z
    assert x is not w
    assert z is not w
    assert x.prop == 'prop 0'
    assert y.prop == 'prop 0'
    assert z.prop == 'prop 1'
    assert x.num_calls == 1
    assert z.num_calls == 1
    assert w.num_calls == 0


class CachedPropertyDummy:
    """A dummy class to test cached_property."""

    def __init__(self, value):
        # type: (int) -> None
        self.value = value
        self.add_one_called = False
        self.add_two_called = False

    @cached_property('value')
    def add_one(self):
        # type: () -> int
        """Add one to value."""
        self.add_one_called = True
        return self.value + 1

    @cached_property('add_one')
    def add_two(self):
        # type: () -> int
        """Add two to value."""
        self.add_two_called = True
        return self.add_one + 1


def test_cached_property_basic():
    # type: () -> None
    """Test cached_property."""
    obj1 = CachedPropertyDummy(1)
    assert not obj1.add_one_called
    assert obj1.add_one == 2, obj1.add_one
    assert obj1.add_one_called
    obj1.add_one_called = False
    assert not obj1.add_one_called
    assert obj1.add_one == 2
    assert not obj1.add_one_called
    obj1.add_one = 0
    assert obj1.add_one == 0
    assert not obj1.add_one_called
    obj1.value = 2
    assert obj1.value == 2
    assert not obj1.add_one_called
    assert obj1.add_one == 3
    assert obj1.add_one_called
    obj1.add_one_called = False
    assert not obj1.add_one_called
    assert obj1.add_one == 3
    assert not obj1.add_one_called
    obj2 = CachedPropertyDummy(4)
    assert obj2.add_one == 5, obj2.add_one
    assert obj2.add_one == 5, obj2.add_one


def test_cached_property_chained():
    # type: () -> None
    """Test cached_property chains."""
    obj = CachedPropertyDummy(10)
    assert not obj.add_one_called
    assert not obj.add_two_called
    assert obj.add_one == 11
    assert obj.add_one_called
    assert not obj.add_two_called
    obj.add_one_called = False
    assert obj.add_one == 11
    assert not obj.add_one_called
    assert not obj.add_two_called
    assert obj.add_two == 12
    assert not obj.add_one_called
    assert obj.add_two_called
    obj.add_two_called = False
    assert obj.add_two == 12
    assert not obj.add_one_called
    assert not obj.add_two_called
    obj.value = 0
    assert not obj.add_one_called
    assert not obj.add_two_called
    assert obj.add_two == 2
    assert obj.add_one_called
    assert obj.add_two_called
    obj.add_one_called = False
    obj.add_two_called = False
    assert obj.add_one == 1
    assert not obj.add_one_called
    assert not obj.add_two_called
