"""A root class with default dunder methods."""

from functools import cached_property, total_ordering
from typing import Any


@total_ordering
class RootClass:
    """A root class with default dunder methods."""

    def __init__(self):
        # type: () -> None
        self._hash = None # type: int

    def __hash__(self):
        # type: () -> int
        if self._hash is None:
            self._hash = self.calculate_hash()
        return self._hash

    def __eq__(self, other):
        # type: (Any) -> bool
        return isinstance(other, type(self)) and self.init_args == other.init_args

    def __lt__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.init_args < other.init_args

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        args_str = ', '.join(repr(arg) for arg in self.init_args)
        return f'{type(self).__name__}({args_str})'

    def calculate_hash(self):
        # type: () -> int
        """Calculate the hash without using cached methods/properties."""
        raise NotImplementedError

    @cached_property
    def init_args(self):
        # type: () -> tuple[Any, ...]
        """Return the init arguments as a tuple."""
        raise NotImplementedError()
