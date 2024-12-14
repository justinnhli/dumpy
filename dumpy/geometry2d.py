"""2D geometry objects."""

from collections import defaultdict, Counter
from collections.abc import Sequence
from enum import IntEnum
from math import inf as INF, copysign, nextafter
from typing import Any, Optional, Union

from .data_structures import SortedDict, PriorityQueue
from .matrix import Matrix, Point2D


class Segment:
    """A line segment."""

    def __init__(self, point1, point2):
        # type: (Matrix, Matrix) -> None
        if (point1.x, point1.y) > (point2.x, point2.y):
            point1, point2 = point2, point1
        self.point1 = point1
        self.point2 = point2

    @property
    def min_x(self):
        # type: () -> float
        """The smaller x-coordinate."""
        return self.point1.x

    @property
    def max_x(self):
        # type: () -> float
        """The larger x-coordinate."""
        return self.point2.x

    @property
    def min_y(self):
        # type: () -> float
        """The smaller y-coordinate."""
        return min(self.point1.y, self.point2.y)

    @property
    def max_y(self):
        # type: () -> float
        """The larger y-coordinate."""
        return max(self.point1.y, self.point2.y)

    @property
    def slope(self):
        # type: () -> float
        """The slope of the segment."""
        denominator = self.point2.x - self.point1.x
        if denominator == 0:
            return float('Inf')
        else:
            return (self.point2.y - self.point1.y) / denominator

    def __hash__(self):
        # type: () -> int
        return hash(self.to_tuple())

    def __eq__(self, other):
        # type: (Any) -> bool
        if not isinstance(other, type(self)):
            return False
        return self.to_tuple() == other.to_tuple()

    def __lt__(self, other):
        # type: (Any) -> bool
        assert isinstance(other, type(self))
        return self.to_tuple() < other.to_tuple()

    def __iter__(self):
        # type: () -> Iterator[Matrix]
        yield self.point1
        yield self.point2

    def __str__(self):
        # type: () -> str
        return repr(self)

    def __repr__(self):
        # type: () -> str
        return f'{type(self).__name__}{self.to_tuple()}'

    def is_parallel(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is parallel."""
        return self.slope == other.slope

    def is_colinear(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment is colinear."""
        return Segment(self.point1, other.point1).slope == self.slope

    def is_kissing(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment intersects at an endpoint."""
        return (
            self.point1 in (other.point1, other.point2)
            or self.point2 in (other.point2, other.point2)
        )

    def is_overlapping(self, other):
        # type: (Segment) -> bool
        """Return whether the other segment overlaps at more than one point."""
        return (
            self.is_colinear(other)
            and (
                self.contains(other.point1, include_end=False)
                or self.contains(other.point2, include_end=False)
            )
        )

    @staticmethod
    def _orientation(p1, p2, p3):
        # type: (Matrix, Matrix, Matrix) -> int
        """Determine the orientation going from p1 to p2 to p3."""
        val = (
            ((p2.y - p1.y) * (p3.x - p2.x))
            - ((p2.x - p1.x) * (p3.y - p2.y))
        )
        if val < 0: # counterclockwise
            return -1
        elif val > 0: # clockwise
            return 1
        else: # co-linear
            return 0

    def contains(self, point, include_end=True):
        # type: (Matrix, bool) -> bool
        """Return True if the point is on the segment."""
        if include_end:
            return (
                (point.x <= max(self.point1.x, self.point2.x))
                and (point.x >= min(self.point1.x, self.point2.x))
                and (point.y <= max(self.point1.y, self.point2.y))
                and (point.y >= min(self.point1.y, self.point2.y))
            )
        else:
            return (
                (point.x < max(self.point1.x, self.point2.x))
                and (point.x > min(self.point1.x, self.point2.x))
                and (point.y < max(self.point1.y, self.point2.y))
                and (point.y > min(self.point1.y, self.point2.y))
            )

    def intersect(self, other, include_end=True):
        # type: (Segment, bool) -> Optional[Matrix]
        """Find the intersection with another segment, if any."""
        bounding_box_overlaps = (
            (
                self.min_x <= other.min_x <= self.max_x
                or other.min_x <= self.min_x <= other.max_x
            ) and (
                self.min_y <= other.min_y <= self.max_y
                or other.min_y <= self.min_y <= other.max_y
            )
        )
        if not bounding_box_overlaps:
            return None
        o1 = Segment._orientation(self.point1, other.point1, other.point2)
        o2 = Segment._orientation(self.point2, other.point1, other.point2)
        o3 = Segment._orientation(other.point1, self.point1, self.point2)
        o4 = Segment._orientation(other.point2, self.point1, self.point2)
        # general case: no co-linearity
        if 0 not in (o1, o2, o3, o4):
            if self.is_parallel(other):
                return None
            vector1 = self.point2 - self.point1
            vector2 = other.point2 - other.point1
            perpendicular1 = Point2D(-vector2.y, vector2.x)
            proportion1 = (other.point1 - self.point1).dot(perpendicular1) / vector1.dot(perpendicular1)
            perpendicular2 = Point2D(-vector1.y, vector1.x)
            proportion2 = (self.point1 - other.point1).dot(perpendicular2) / vector2.dot(perpendicular2)
            if 0 <= proportion1 <= 1 and 0 <= proportion2 <= 1:
                if include_end or (proportion1 not in (0, 1) and proportion2 not in (0, 1)):
                    return self.point1 + vector1 * proportion1
            return None
        if not include_end:
            return None
        if o1 == 0 and other.contains(self.point1, include_end=True):
            # p1, q1 and p2 are collinear and p2 lies on segment p1q1
            return self.point1
        elif o2 == 0 and other.contains(self.point2, include_end=True):
            # p1, q1 and q2 are collinear and q2 lies on segment p1q1
            return self.point2
        elif o3 == 0 and self.contains(other.point1, include_end=True):
            # p2, q2 and p1 are collinear and p1 lies on segment p2q2
            return other.point1
        elif o4 == 0 and self.contains(other.point2, include_end=True):
            # p2, q2 and q1 are collinear and q1 lies on segment p2q2
            return other.point2
        else:
            return None

    def to_tuple(self):
        # type: () -> tuple[Any, ...]
        """Convert to a tuple."""
        return (self.point1.to_tuple(), self.point2.to_tuple())

    @staticmethod
    def from_tuple(value):
        # type: () -> Segment
        """Create from a tuple."""
        return Segment(
            Matrix.from_tuple(value[0]),
            Matrix.from_tuple(value[1]),
        )


def bentley_ottmann(segments, include_end=False, ndigits=9): # pylint: disable = too-many-statements
    # type: (Sequence[Segment], bool, int) -> list[Matrix]
    """Implement the Bentley-Ottmann all intersects algorithm.

    The Bentley-Ottmann algorithm is a sweep line algorithm for finding all
    intersects of given segments. Using a vertical sweep line over the 
    endpoints of the segments (in a priority queue), it additionally uses a
    balanced binary search tree to track the y-values of each segment. Only
    the intersects of adjacent segments are calculated and added to the
    priority queue. At every endpoint and intersect, the tree is updated,
    and the appropriate events added and  removed from the priority queue.
    This allows the algorithm to have O((n + k)log(n)) complexity, where n
    is the number of segments and k the number of intersects.

    The heart of the algorithm is updating the tree to determine segments
    are adjacent. This is complicated because every segment could have new
    y-values, but the complexity requires only log(n) of them be updated at
    every endpoint/intersect. The naive way of doing this - looping over all
    segments in the tree - would require O(n^2) time. This can be seen in
    the case of n parallel segments, as each new segment requires updating
    all previous segments. Instead, the trick is to recognize that the order
    of the segments cannot change during this update, as otherwise we would
    have had a "meet" event first. The correct way to do this is therefore 
    to do update the keys ONLY OF SEGMENTS ON THE PATH DOWN FROM THE ROOT TO
    THE NEW LEAF. The tree would lose the binary search tree property, but
    that's okay, because:

    * since the order doesn't change, updating the key would never point to
      the incorrect child, even if the un-updated child ends up on the
      "wrong" side of its parent
    * the keys that are not updated are, by definition, irrelevant for the
      purpose of determining the intersects of the new segment, although the
      previous and next nodes may need to be updated as well
    * when those un-updated keys are needed, it will either be due to a new
      segment (dealt with above) or a crossing, at which point they can be
      swapped without affecting the order of anything else in the tree
    * when rotating on the way back up after insertion, some additional keys
      may need to be updated, but only O(log n) keys in the worst case, and
      again the order does not change

    In other words, because the relevant keys are updated when necessary,
    the tree can be considered "eventual consistent" (to borrow from
    database terminology). This relaxation of the binary search tree
    property allows for insertion, search, and removal to all remain
    O(log n), and the overall Bentley-Ottmann algorithm to remain
    O((n + k)log(n))

    This implementation assumes that segments do not overlap, but otherwise
    deals with intersections of endpoints, intersections of three of more
    segments, vertical segments, and other edge cases. This is supported by
    a two modifications to the basic algorithm:

    * intersects also record which segments generated them, and intersects
      of more than two segments are merged and dealt with simultaneously

    * orderings of segments and intersects use additional properties to
      accommodate kissing and vertical segments
    """

    class BOEvent(IntEnum):
        """Enum for different Bentley-Ottmann events."""
        START = 1
        MEET = 2
        END = 3


    class BOSegmentWrapper:
        """A wrapper class for ordering Segments."""

        sweep_x = None

        def __init__(self, segment):
            # type: (Segment) -> None
            self.segment = segment
            self._x = None # type: Optional[float]
            self._y = None # type: Optional[float]

        @property
        def key(self):
            # type: () -> tuple[float, float, Segment]
            """Return the comparison key."""
            return (self.y, -self.segment.slope, self.segment)

        @property
        def y(self):
            # type: () -> float
            """Return the correct y value at BOSegmentWrapper.sweep_x."""
            if self._x != BOSegmentWrapper.sweep_x:
                self._update_y()
            return self._y

        @y.setter
        def y(self, value):
            # type: (float) -> None
            """Set the value of y forcefully."""
            self._x = BOSegmentWrapper.sweep_x
            self._y = value

        def __eq__(self, other):
            # type: (Any) -> bool
            return self.key == other.key

        def __lt__(self, other):
            # type: (Any) -> bool
            return self.key < other.key

        def _update_y(self):
            # type: () -> None
            self._x = BOSegmentWrapper.sweep_x
            if self.segment.point1.x == self.segment.point2.x:
                if self._y is None:
                    self._y = self.segment.min_y
            else:
                dx = self._x - self.segment.point1.x
                self._y = self.segment.point1.y + dx * self.segment.slope

    # initialize the two main data structures
    priority_queue = PriorityQueue() # type: PriorityQueue[tuple[float, int, float], tuple[str, Union[Segment, Matrix]]]
    tree = SortedDict() # type: SortedDict[BOSegmentWrapper, Segment]
    for segment in segments:
        priority_queue.push(
            (BOEvent.START, segment),
            (segment.min_x, BOEvent.START, segment.point1.y),
        )
        priority_queue.push(
            (BOEvent.END, segment),
            (segment.max_x, BOEvent.END, segment.point2.y),
        )
    # initialize additional FIXME keeping structures
    segment_wrappers = {} # type: dict[Segment, BOSegmentWrapper]
    intersect_cache = {} # type: dict[tuple[Segment, Segment], tuple[float, bool]]
    intersect_segment_counts = defaultdict(Counter) # type: dict[Matrix, Counter[Segment]]
    segment_intersect_map = defaultdict(dict) # type: dict[Segment, dict[Matrix, bool]]

    def get_intersect(segment1, segment2):
        # type: (Segment, Segment) -> Matrix
        # need to deal with all intersects, including ends, to keep tree in order
        if segment1.to_tuple() < segment2.to_tuple():
            intersect_key = (segment1, segment2)
        else:
            intersect_key = (segment2, segment1)
        if intersect_key not in intersect_cache:
            intersect = segment1.intersect(segment2, include_end=True)
            intersect_cache[intersect_key] = intersect
            if intersect:
                intersect = round(intersect, ndigits=ndigits)
                intersect_cache[intersect_key] = intersect
                intersect_tuple = intersect.to_tuple()
                segment_intersect_map[segment1][intersect_tuple] = (
                    intersect not in (segment1.point1, segment1.point2)
                )
                segment_intersect_map[segment2][intersect_tuple] = (
                    intersect not in (segment2.point1, segment2.point2)
                )
        return intersect_cache[intersect_key]

    def get_tree_neighbors(segment):
        # type: (Segment) -> list[Segment]
        cursor = tree.cursor(segment_wrappers[segment])
        neighbors = []
        if cursor.has_prev:
            neighbors.append(cursor.prev().value)
        if cursor.has_next:
            neighbors.append(cursor.next().value)
        return neighbors

    def schedule_intersect(segment1, segment2):
        # type: (Segment, Segment) -> None
        intersect = get_intersect(segment1, segment2)
        if not intersect:
            return
        # check that intersection is after sweep line
        if intersect.x < BOSegmentWrapper.sweep_x:
            return
        intersect_tuple = intersect.to_tuple()
        if intersect_segment_counts[intersect_tuple].total() == 0:
            priority_queue.push(
                (BOEvent.MEET, intersect),
                (intersect.x, BOEvent.MEET, intersect.y),
            )
        intersect_segment_counts[intersect_tuple][segment1] += 1
        intersect_segment_counts[intersect_tuple][segment2] += 1

    def unschedule_intersect(segment1, segment2):
        # type: (Segment, Segment) -> None
        intersect = get_intersect(segment1, segment2)
        if not intersect:
            return
        if intersect.x <= BOSegmentWrapper.sweep_x:
            return
        intersect_tuple = intersect.to_tuple()
        intersect_segment_counts[intersect_tuple][segment1] -= 1
        intersect_segment_counts[intersect_tuple][segment2] -= 1
        if intersect_segment_counts[intersect_tuple].total() == 0:
            priority_queue.remove(
                (BOEvent.MEET, intersect),
                (intersect.x, BOEvent.MEET, intersect.y),
            )

    def insert_into_tree(segment):
        # type: (Segment) -> None
        segment_key = BOSegmentWrapper(segment)
        segment_wrappers[segment] = segment_key
        tree[segment_key] = segment
        # get neighbors
        neighbors = get_tree_neighbors(segment)
        # remove old intersects from the priority queue
        if len(neighbors) == 2:
            unschedule_intersect(*neighbors) # pylint: disable = no-value-for-parameter
        # insert new intersects into the priority queue (if not already inserted)
        for neighbor in neighbors:
            schedule_intersect(segment, neighbor)

    def remove_from_tree(segment):
        # type: (Segment) -> None
        # get neighbors
        neighbors = get_tree_neighbors(segment)
        # remove intersects from the priority queue
        for neighbor in neighbors:
            unschedule_intersect(segment, neighbor)
        # insert "uncovered" intersect from the priority queue
        if len(neighbors) == 2:
            schedule_intersect(*neighbors) # pylint: disable = no-value-for-parameter
        # remove from tree
        del tree[segment_wrappers[segment]]

    def swap(*segments):
        # type: (*Segment) -> None
        # arrange segments by increasing slope
        segments = tuple(sorted(
            segments,
            key=(lambda segment: (-segment.slope, segment.min_x, segment.min_y)), # pylint: disable = superfluous-parens
        ))
        # manually update the SegmentWrappers to avoid floating point precision issues
        intersect = get_intersect(*segments[:2])
        steps = list(range(-(len(segments) // 2), len(segments) // 2 + 1))
        if len(segments) % 2 == 0:
            steps.remove(0)
        for segment, step in zip(segments, steps):
            segment_wrappers[segment].y = nextafter(
                intersect.y,
                copysign(INF, step),
                steps=abs(step),
            )
        # update intersects with surrounding segments
        cursor_head = tree.cursor(segment_wrappers[segments[0]])
        if cursor_head.has_prev:
            segment_prev = cursor_head.prev().value
            unschedule_intersect(segment_prev, segments[0])
            schedule_intersect(segment_prev, segments[-1])
        cursor_tail = tree.cursor(segment_wrappers[segments[-1]])
        if cursor_tail.has_next:
            segment_next = cursor_tail.next().value
            unschedule_intersect(segments[-1], segment_next)
            schedule_intersect(segments[0], segment_next)
        # reverse the segments in the tree
        curr_cursor = cursor_head
        for segment, step in zip(reversed(segments), steps):
            segment_wrappers[segment].y = nextafter(
                intersect.y,
                copysign(INF, step),
                steps=abs(step),
            )
            curr_cursor.node.key = segment_wrappers[segment]
            curr_cursor.node.value = segment
            if curr_cursor.has_next:
                curr_cursor = curr_cursor.next()

    def non_endpoint_intersect(intersect):
        # type: (Matrix) -> bool
        intersect_tuple = intersect.to_tuple()
        count = 0
        for segment in intersect_segment_counts[intersect.to_tuple()]:
            if segment_intersect_map[segment][intersect_tuple]:
                count += 1
                if count == 2:
                    return True
        return False

    results = [] # type: list[Matrix]
    while priority_queue:
        (sweep_x, *_), (event_type, data) = priority_queue.pop()
        BOSegmentWrapper.sweep_x = sweep_x
        if event_type == BOEvent.START:
            segment = data
            insert_into_tree(segment)
        elif event_type == BOEvent.END:
            segment = data
            remove_from_tree(segment)
        elif event_type == BOEvent.MEET:
            intersect = data
            if include_end or non_endpoint_intersect(intersect):
                results.append(intersect)
            swap(*intersect_segment_counts[intersect.to_tuple()])
    return results
