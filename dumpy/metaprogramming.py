"""Utility code for metaprogramming."""

from collections import namedtuple
from functools import lru_cache, wraps
from typing import Any, Callable, Self


def cached_class(cls, max_size=1024):
    """Cache instances of classes based on initialization arguments.

    Adapted from https://stackoverflow.com/questions/75453502/caching-python-class-instances
    """

    @wraps(cls.__new__)
    def __new__(cls, *args, **kwargs):
        return cls.__cache__(cls, args, tuple(sorted(kwargs.items())))

    @lru_cache(max_size)
    def __cache__(cls, args, kwargs):
        return cls.__orig_new__(cls, *args, **dict(kwargs))

    cls.__cache__ = __cache__
    cls.__orig_new__ = cls.__new__
    cls.__new__ = __new__
    return cls


CachedValue = namedtuple('CachedValue', 'cache, value')


class cached_property: # pylint: disable = invalid-name
    """Descriptor to cache properties of classes."""

    def __init__(self, *upstream_attrs):
        # type: (*str) -> None
        if not all(isinstance(attr, str) for attr in upstream_attrs):
            raise ValueError(' '.join([
                'arguments to cached_property should be strs;',
                'did you do @cached_property instead of @cached_property()?',
            ]))
        self.function = None # type: Callable[..., Any]
        self.function_name = ''
        self.upstream_attrs = upstream_attrs

    def __call__(self, function):
        # type: (Callable[..., Any]) -> Self
        self.function = function
        self.__doc__ = self.function.__doc__
        self.function_name = self.function.__name__
        return self

    def __get__(self, obj, objtype=None):
        # type: (Any, Any) -> Any
        if obj is None:
            return self
        if not hasattr(obj, '_cached_properties'):
            obj._cached_properties = {}
        upstream_vals = self.collect_upstream_vals(obj)
        cached_vals, value = obj._cached_properties.get(self.function_name, (None, None))
        if cached_vals != upstream_vals:
            value = self.function(obj)
            obj._cached_properties[self.function_name] = CachedValue(
                upstream_vals, value,
            )
        return value

    def __set__(self, obj, value):
        # type: (Any, Any) -> None
        obj._cached_properties[self.function_name] = CachedValue(
            self.collect_upstream_vals(obj),
            value,
        )

    def __delete__(self, obj):
        # type: (Any) -> None
        raise AttributeError(' '.join([
            f"cannot delete attribute '{self.function.__name__}'",
            f"of '{obj.__class__.__name__}' objects",
        ]))

    def collect_upstream_vals(self, obj):
        # type: (Any) -> tuple[Any, ...]
        """Create a dictionary of upstream values."""
        return tuple(getattr(obj, attr) for attr in self.upstream_attrs)

    def is_cached(self, obj):
        # type: (Any) -> bool
        return (
            hasattr(obj, '_cached_properties')
            and self.function_name in obj._cached_properties
        )
