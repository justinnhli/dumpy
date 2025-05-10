from dumpy.metaprogramming import cached_class, cached_property


@cached_class
class Dummy:

    def __init__(self, x):
        self.x = x
        self.num_calls = 0

    @cached_property('x')
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


class CPTest1:

    def __init__(self, value):
        # type: (int) -> None
        self.value = value
        self.called = False

    @cached_property('value')
    def add_one(self):
        # type: () -> int
        self.called = True
        return self.value + 1


class CPTest2:

    def __init__(self, value):
        self.value = value
        self.add_one_called = False
        self.add_two_called = False

    @cached_property('value')
    def add_one(self):
        self.add_one_called = True
        return self.value + 1

    @cached_property('add_one')
    def add_two(self):
        self.add_two_called = True
        return self.add_one + 1


def test_cached_property_basic():
    # type: () -> None
    obj1 = CPTest1(1)
    assert not obj1.called
    assert obj1.add_one == 2, obj1.add_one
    assert obj1.called
    obj1.called = False
    assert not obj1.called
    assert obj1.add_one == 2
    assert not obj1.called
    obj1.add_one = 0
    assert obj1.add_one == 0
    assert not obj1.called
    obj1.value = 2
    assert obj1.value == 2
    assert not obj1.called
    assert obj1.add_one == 3
    assert obj1.called
    obj1.called = False
    assert not obj1.called
    assert obj1.add_one == 3
    assert not obj1.called
    obj2 = CPTest1(4)
    assert obj2.add_one == 5, obj2.add_one
    assert obj2.add_one == 5, obj2.add_one


def test_cached_property_chained():
    obj = CPTest2(10)
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
