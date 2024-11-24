"""Tests for data_structures.py."""

from itertools import permutations

from dumpy.data_structures import UnionFind, SortedDict, SortedSet, PriorityQueue


def test_unionfind():
    """Test UnionFind."""
    assert not UnionFind()
    union_find = UnionFind(range(4))
    assert all(i in union_find for i in range(len(union_find)))
    assert set(union_find) == set(range(4))
    for i in range(4, 8):
        union_find.add(i)
    assert all(union_find[i] == i for i in range(len(union_find)))
    for i in range(1, 8, 2):
        union_find.union(1, i)
    assert all(union_find.same(5, i) for i in range(1, 8, 2))
    assert set(union_find[i] for i in range(0, 8, 2)) == set(range(0, 8, 2))


def test_sorteddict():
    """Test SortedDict."""
    # pylint: disable = use-implicit-booleaness-not-comparison
    sorted_dict = SortedDict()
    assert 0 not in sorted_dict
    assert list(sorted_dict) == list(sorted_dict.keys()) == list(sorted_dict.values()) == list(sorted_dict.items()) == []
    size = 7
    # map check
    for permutation in permutations(range(size)):
        sorted_dict = SortedDict()
        for key in permutation:
            sorted_dict[key] = key * key
        assert len(sorted_dict) == size
        assert list(e for e in sorted_dict) == list(range(size))
        assert list(sorted_dict.items()) == list((num, num * num) for num in range(size))
        for num in range(size):
            assert num in sorted_dict
            assert sorted_dict[num] == num * num
        for num in range(size):
            del sorted_dict[num]
            assert len(sorted_dict) == size - num - 1
    src_dict = {num: num * num for num in range(101)}
    assert SortedDict.from_dict(src_dict).to_dict() == src_dict
    # defaultdict check
    sorted_dict = SortedDict(factory=set)
    for i in range(10):
        for j in range(i, i + 5):
            sorted_dict[i].add(j)
    for i in range(10):
        assert sorted_dict[i] == set(range(i, i + 5))
    sorted_dict.clear()
    assert len(sorted_dict) == 0
    assert list(sorted_dict) == []
    # bug discovered 2020-06-05
    sorted_dict = SortedDict()
    for i in [5, 2, 9, 1, 4, 7, 11, 0, 3, 6, 8, 10, 12]:
        sorted_dict[i] = str(i)
    del sorted_dict[5]
    assert list(sorted_dict.keys()) == [*range(5), *range(6, 13)]

def test_sortedset():
    """Test SortedSet."""
    size = 7
    # set check
    for permutation in permutations(range(size)):
        sorted_set = SortedSet()
        for element in permutation:
            sorted_set.add(element)
        assert len(sorted_set) == size
        assert list(e for e in sorted_set) == list(range(size))
        assert list(reversed(sorted_set)) == list(reversed(range(size)))
        for num in range(size):
            assert num in sorted_set
        for num in range(size):
            sorted_set.discard(num)
            assert len(sorted_set) == size - num - 1
            assert list(e for e in sorted_set) == list(range(num + 1, size))
    src_set = set(range(101))
    assert SortedSet.from_set(src_set).to_set() == src_set
