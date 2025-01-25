from functools import cached_property

from dumpy.metaprogramming import cached_class


@cached_class
class Dummy:

    def __init__(self, x):
        self.x = x
        self.num_calls = 0

    @cached_property
    def prop(self):
        self.num_calls += 1
        return f'prop {self.x}'


def test_cached_class():
    x = Dummy(0)
    y = Dummy(0)
    z = Dummy(1)
    w = Dummy(2)
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
