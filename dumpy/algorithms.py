"""Utility algorithms."""

from collections import defaultdict, Counter
from collections.abc import Sequence
from enum import IntEnum
from math import inf as INF, copysign, nextafter
from typing import Any, Optional, Union

from .data_structures import SortedDict, PriorityQueue
from .matrix import Matrix
from .primitives import Segment


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

        sweep_x = None # type: float

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

    Priority = tuple[float, int, float]

    # initialize the two main data structures
    priority_queue = PriorityQueue() # type: PriorityQueue[Priority, tuple[BOEvent, Union[Segment, Matrix]]]
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
    intersect_cache = {} # type: dict[tuple[Segment, Segment], Matrix]
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
                segment_intersect_map[segment1][intersect] = (
                    intersect not in (segment1.point1, segment1.point2)
                )
                segment_intersect_map[segment2][intersect] = (
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
        if intersect_segment_counts[intersect].total() == 0:
            priority_queue.push(
                (BOEvent.MEET, intersect),
                (intersect.x, BOEvent.MEET, intersect.y),
            )
        intersect_segment_counts[intersect][segment1] += 1
        intersect_segment_counts[intersect][segment2] += 1

    def unschedule_intersect(segment1, segment2):
        # type: (Segment, Segment) -> None
        intersect = get_intersect(segment1, segment2)
        if not intersect:
            return
        if intersect.x <= BOSegmentWrapper.sweep_x:
            return
        intersect_segment_counts[intersect][segment1] -= 1
        intersect_segment_counts[intersect][segment2] -= 1
        if intersect_segment_counts[intersect].total() == 0:
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
        count = 0
        for segment in intersect_segment_counts[intersect]:
            if segment_intersect_map[segment][intersect]:
                count += 1
                if count == 2:
                    return True
        return False

    results = [] # type: list[Matrix]
    while priority_queue:
        (sweep_x, *_), (event_type, data) = priority_queue.pop()
        BOSegmentWrapper.sweep_x = sweep_x
        if event_type == BOEvent.START:
            assert isinstance(data, Segment)
            insert_into_tree(data)
        elif event_type == BOEvent.END:
            assert isinstance(data, Segment)
            remove_from_tree(data)
        elif event_type == BOEvent.MEET:
            assert isinstance(data, Matrix)
            intersect = data
            if include_end or non_endpoint_intersect(intersect):
                results.append(intersect)
            swap(*intersect_segment_counts[intersect])
    return results
