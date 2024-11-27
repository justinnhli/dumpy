"""Utility data structures."""

from typing import Any, Optional, Union
from typing import Callable, Collection, Iterable, Mapping, Iterator
from typing import TypeVar, Generic
from collections.abc import MutableSet, Hashable

from .utilitypes import ComparableT


KT = TypeVar('KT', bound=ComparableT)
VT = TypeVar('VT')


class UnionFind:
    """UnionFind for discrete sets."""

    def __init__(self, nodes=None):
        # type: (Optional[Iterable[Hashable]]) -> None
        """Initialize the UnionFind."""
        if nodes is None:
            nodes = []
        self.parents = {node: node for node in nodes}

    def __len__(self):
        # type: () -> int
        return len(self.parents)

    def __contains__(self, node):
        # type: (Hashable) -> bool
        return node in self.parents

    def __getitem__(self, node):
        # type: (Hashable) -> Hashable
        path = []
        while self.parents[node] != node:
            path.append(node)
            node = self.parents[node]
        path.append(node)
        rep = path[-1]
        for step in path:
            self.parents[step] = rep
        return rep

    def __iter__(self):
        # type: () -> Iterator[Hashable]
        return iter(self.parents)

    def __bool__(self):
        # type: () -> bool
        return bool(self.parents)

    def union(self, node1, node2):
        # type: (Hashable, Hashable) -> None
        """Join two discrete sets."""
        self.add(node1)
        rep1 = self[node1]
        self.add(node2)
        rep2 = self[node2]
        self.parents[rep2] = rep1

    def same(self, node1, node2):
        # type: (Hashable, Hashable) -> bool
        """Check if two members are in the same set."""
        return self[node1] == self[node2]

    def add(self, node, parent=None):
        # type: (Hashable, Optional[Hashable]) -> bool
        """Add a node."""
        if node in self.parents:
            return False
        if parent is None:
            parent = node
        self.parents[node] = parent
        return True


class _AVLNode(Generic[KT, VT]):
    """An AVL tree node."""

    def __init__(self, key, value, prev_node=None, next_node=None):
        # type: (KT, VT, _AVLNode[KT, VT], _AVLNode[KT, VT]) -> None
        """Initialize the _AVLNode."""
        self.key = key # type: KT
        self.value = value # type: VT
        self.left = None # type: Optional[_AVLNode[KT, VT]]
        self.right = None # type: Optional[_AVLNode[KT, VT]]
        self.prev = prev_node # type: Optional[_AVLNode[KT, VT]]
        if self.prev is not None:
            self.prev.next = self
        self.next = next_node # type: Optional[_AVLNode[KT, VT]]
        if self.next is not None:
            self.next.prev = self
        self.height = 1
        self.balance = 0

    def update_metadata(self):
        # type: () -> None
        """Update the height and balance of the node."""
        left_height = (self.left.height if self.left else 0)
        right_height = (self.right.height if self.right else 0)
        self.height = max(left_height, right_height) + 1
        self.balance = right_height - left_height


class SortedDict(Mapping[KT, VT]):
    # pylint: disable = too-many-public-methods
    """A sorted dictionary backed by an AVL tree."""

    def __init__(self, factory=None):
        # type: (Callable[[], VT]) -> None
        """Initialize the SortedDict."""
        self.factory = factory
        self.size = 0
        self.root = None # type: Optional[_AVLNode[KT, VT]]
        self.head = None # type: Optional[_AVLNode[KT, VT]]
        self.tail = None # type: Optional[_AVLNode[KT, VT]]
        self._content_hash = None # type: Optional[int]

    def __bool__(self):
        # type: () -> bool
        return self.size != 0

    def __eq__(self, other):
        # type: (Any) -> bool
        if self is other:
            return True
        if type(self) is not type(other):
            return False
        if len(self) != len(other):
            return False
        return all(
            pair1 == pair2 for pair1, pair2
            in zip(self.items(), other.items())
        )

    def __lt__(self, other):
        # type: (Any) -> bool
        for pair1, pair2 in zip(self.items(), other.items()):
            if pair1 < pair2:
                return True
            if pair1 > pair2:
                return False
        return len(self) < len(other)

    def __len__(self):
        # type: () -> int
        return self.size

    def __contains__(self, key):
        # type: (KT) -> bool
        return self._get_node(key) is not None

    def __iter__(self):
        # type: () -> Iterator[KT]
        node = self.head
        while node is not None:
            yield node.key
            node = node.next

    def __setitem__(self, key, value):
        # type: (KT, VT) -> None
        self._put(key, value)

    def __getitem__(self, key):
        # type: (KT) -> VT
        node = self._get_node(key)
        if node is not None:
            return node.value
        if self.factory is None:
            raise KeyError(key)
        result = self.factory()
        self[key] = result
        return result

    def __delitem__(self, key):
        # type: (KT) -> None
        self._del(key)

    def __reversed__(self):
        # type: () -> Iterator[KT]
        node = self.tail
        while node is not None:
            yield node.key
            node = node.prev

    def __repr__(self):
        # type: () -> str
        return 'SortedDict(' + ', '.join(f'{k}={v}' for k, v in self.items()) + ')'

    def __str__(self):
        # type: () -> str
        return 'SortedDict(' + ', '.join(f'{k}={v}' for k, v in self.items()) + ')'

    @property
    def contents_hash(self):
        # type: () -> int
        """Get a hash of the contents.

        Note: this hash will change if the contents of this SortedDict changes.
        """
        if self._content_hash is None:
            self._content_hash = hash(tuple(self.items()))
        return self._content_hash

    def _put_helper(self, key, value, node=None, prev_node=None, next_node=None):
        # type: (KT, VT, _AVLNode[KT, VT], _AVLNode[KT, VT], _AVLNode[KT, VT]) -> _AVLNode[KT, VT]
        if node is None:
            self.size += 1
            new_node = _AVLNode[KT, VT](key, value, prev_node, next_node)
            if prev_node is None:
                self.head = new_node
            if next_node is None:
                self.tail = new_node
            return new_node
        if key == node.key:
            node.value = value
            return node
        if key < node.key:
            node.left = self._put_helper(key, value, node.left, prev_node, node)
        else:
            node.right = self._put_helper(key, value, node.right, node, next_node)
        return self._balance(node)

    def _put(self, key, value):
        # type: (KT, VT) -> None
        self.root = self._put_helper(key, value, self.root, None, None)
        self._content_hash = None

    @staticmethod
    def _get_node_helper(key, node=None):
        # type: (KT, _AVLNode[KT, VT]) -> Optional[_AVLNode[KT, VT]]
        if node is None:
            return None
        elif key < node.key:
            return SortedDict._get_node_helper(key, node.left)
        elif node.key < key:
            return SortedDict._get_node_helper(key, node.right)
        else:
            return node

    def _get_node(self, key):
        # type: (KT) -> Optional[_AVLNode[KT, VT]]
        return SortedDict._get_node_helper(key, self.root)

    def _del_helper(self, key, node=None):
        # type: (KT, _AVLNode[KT, VT]) -> tuple[Optional[_AVLNode[KT, VT]], VT]
        # pylint: disable = too-many-branches
        value = None
        if node is None:
            raise KeyError(key)
        if key < node.key:
            node.left, value = self._del_helper(key, node.left)
        elif node.key < key:
            node.right, value = self._del_helper(key, node.right)
        elif node.left is not None:
            assert node.prev is not None
            node.key = node.prev.key
            node.value = node.prev.value
            node.left, value = self._del_helper(node.prev.key, node.left)
        elif node.right is not None:
            assert node.next is not None
            node.key = node.next.key
            node.value = node.next.value
            node.right, value = self._del_helper(node.next.key, node.right)
        else:
            self.size -= 1
            if node.prev is not None:
                node.prev.next = node.next
            else:
                self.head = node.next
            if node.next is not None:
                node.next.prev = node.prev
            else:
                self.tail = node.prev
            return None, node.value
        return self._balance(node), value

    def _del(self, key):
        # type: (KT) -> VT
        self.root, value = self._del_helper(key, self.root)
        self._content_hash = None
        return value

    def _nodes(self):
        # type: () -> Iterator[_AVLNode[KT, VT]]
        node = self.head
        while node is not None:
            yield node
            node = node.next

    def clear(self):
        # type: () -> None
        """Remove all elements from the SortedDict."""
        self.size = 0
        self.root = None
        self.head = None
        self.tail = None
        self._content_hash = None

    @staticmethod
    def _balance(node):
        # type: (_AVLNode[KT, VT]) -> _AVLNode[KT, VT]
        node.update_metadata()
        if node.balance < -1:
            if node.left.balance == 1:
                node.left = SortedDict._rotate_ccw(node.left)
            return SortedDict._rotate_cw(node)
        elif node.balance > 1:
            if node.right.balance == -1:
                node.right = SortedDict._rotate_cw(node.right)
            return SortedDict._rotate_ccw(node)
        else:
            return node

    def setdefault(self, key, default=None):
        # type: (KT, Optional[VT]) -> Optional[VT]
        """Get the value of a key, or set it to the default."""
        node = self._get_node(key)
        if node is None:
            self._put(key, default)
        return node.value

    def update(self, *mappings):
        # type: (*Union[set[tuple[KT, VT]], Mapping[KT, VT]]) -> None
        """Add the key and values to the map, overwriting existing values."""
        for mapping in mappings:
            if isinstance(mapping, Mapping):
                for key, value in mapping.items():
                    self._put(key, value)
            else:
                for key, value in mapping:
                    self._put(key, value)

    def get(self, key, default=None):
        # type: (KT, Optional[VT]) -> Optional[VT]
        """Return the value for the key, or the default if it doesn't exist."""
        node = self._get_node(key)
        if node is None:
            return default
        else:
            return node.value

    def pop(self, key, default=None):
        # type: (KT, Optional[VT]) -> Optional[VT]
        """Remove the key and return the value, or the default if it doesn't exist."""
        try:
            value = self._del(key)
            return value
        except KeyError:
            return default

    def keys(self):
        # type: () -> Iterator[KT]
        """Create a generator of the keys."""
        node = self.head
        while node is not None:
            yield node.key
            node = node.next

    def values(self):
        # type: () -> Iterator[VT]
        """Create a generator of the values."""
        node = self.head
        while node is not None:
            yield node.value
            node = node.next

    def items(self):
        # type: () -> Iterator[tuple[KT, VT]]
        """Create a generator of the key-value pairs."""
        node = self.head
        while node is not None:
            yield node.key, node.value
            node = node.next

    def to_dict(self):
        # type: () -> dict[KT, VT]
        """Return the keys and values in a normal dict."""
        return dict(self.items())

    @staticmethod
    def from_dict(src_dict):
        # type: (Mapping[KT, VT]) -> SortedDict[KT, VT]
        """Create an SortedDict (as a dict) from a dictionary."""
        tree = SortedDict() # type: SortedDict[KT, VT]
        tree.update(src_dict.items())
        return tree

    @staticmethod
    def _rotate_cw(node):
        # type: (_AVLNode[KT, VT]) -> _AVLNode[KT, VT]
        left = node.left
        node.left = left.right
        left.right = node
        node.update_metadata()
        left.update_metadata()
        return left

    @staticmethod
    def _rotate_ccw(node):
        # type: (_AVLNode[KT, VT]) -> _AVLNode[KT, VT]
        right = node.right
        node.right = right.left
        right.left = node
        node.update_metadata()
        right.update_metadata()
        return right


class SortedSet(MutableSet[KT]):
    """A sorted set."""

    def __init__(self):
        # type: () -> None
        """Initialize the SortedSet."""
        self.tree = SortedDict() # type: SortedDict[KT, None]

    def __len__(self):
        # type: () -> int
        return len(self.tree)

    def __contains__(self, key):
        # type: (KT) -> bool
        return key in self.tree

    def __bool__(self):
        # type: () -> bool
        return bool(self.tree)

    def __iter__(self):
        # type: () -> Iterator[KT]
        return iter(self.tree)

    def __reversed__(self):
        # type: () -> Iterator[KT]
        return reversed(self.tree)

    def add(self, value):
        # type: (KT) -> None
        """Add an element to the SortedDict (set)."""
        self.tree[value] = None

    def remove(self, value):
        # type: (KT) -> None
        """Remove an element from the set."""
        del self.tree[value]

    def discard(self, value):
        # type: (KT) -> None
        """Remove an element from the set if it is present."""
        try:
            del self.tree[value]
        except KeyError:
            pass

    def is_disjoint(self, other):
        # type: (Collection[KT]) -> bool
        """Check if the two sets are disjoint."""
        return all((element not in other) for element in self)

    def is_subset(self, other):
        # type: (Collection[KT]) -> bool
        """Check if this is a subset of another set."""
        return (
            len(self) < len(other)
            and all((element in other) for element in self)
        )

    def is_superset(self, other):
        # type: (Collection[KT]) -> bool
        """Check if this is a superset of another set."""
        return (
            len(self) > len(other)
            and all((element in self) for element in other)
        )

    def union(self, *others):
        # type: (*Collection[KT]) -> SortedSet[KT]
        """Create the union of this and other sets."""
        result = SortedSet() # type: SortedSet[KT]
        result.union_update(self, *others)
        return result

    def intersection(self, *others):
        # type: (*Collection[KT]) -> SortedSet[KT]
        """Create the intersection of this and other sets."""
        new_set = SortedSet() # type: SortedSet[KT]
        min_set = others[0]
        for other in others:
            if len(other) < len(min_set):
                min_set = other
        new_set.union_update(min_set)
        new_set.intersection_update(self)
        new_set.intersection_update(*others)
        return new_set

    def difference(self, *others):
        # type: (*Collection[KT]) -> SortedSet[KT]
        """Create the difference of this and other sets."""
        new_set = SortedSet() # type: SortedSet[KT]
        new_set.union_update(self)
        new_set.difference_update(*others)
        return new_set

    def union_update(self, *others):
        # type: (*Collection[KT]) -> None
        """Update this set to be the union of this and other sets."""
        for other in others:
            for element in other:
                self.add(element)

    def intersection_update(self, *others):
        # type: (*Collection[KT]) -> None
        """Keep only the intersection of this and other sets."""
        sorted_others = sorted(others, key=len)
        for element in self:
            if any((element not in other) for other in sorted_others):
                self.remove(element)

    def difference_update(self, *others):
        # type: (*Collection[KT]) -> None
        """Keep only the difference of this and other sets."""
        union = SortedSet() # type: SortedSet[KT]
        union.union_update(*others)
        for element in self:
            if element in union:
                self.remove(element)

    def to_set(self):
        # type: () -> set[KT]
        """Return the elements in a normal set."""
        return set(self)

    @staticmethod
    def from_set(src_set):
        # type: (set[KT]) -> SortedSet[KT]
        """Create an SortedDict (as a set) from a set."""
        result = SortedSet() # type: SortedSet[KT]
        result.union_update(src_set)
        return result
