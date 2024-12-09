"""Tests for geometry2d.py."""

from itertools import product, combinations
from typing import Iterator

from dumpy.geometry2d import Segment, bentley_ottmann
from dumpy.matrix import Matrix, Point2D


def test_segment():
    # at most one point of intersection, include_end=True
    segments = [
        # vertical second segment
        (Segment(Point2D(0, 2), Point2D(0, 4)), (Point2D(0, 2), None)), # parallel, co-linear, end-end
        (Segment(Point2D(1, 2), Point2D(1, 4)), (None, None)), # parallel, not co-linear, not intersecting
        (Segment(Point2D(1, 1), Point2D(1, 3)), (None, None)), # parallel, not co-linear, not intersecting
        (Segment(Point2D(1, 0), Point2D(1, 2)), (None, None)), # parallel, not co-linear, not intersecting
        # horizontal second segment
        (Segment(Point2D(-1, 3), Point2D(1, 3)), (None, None)), # not parallel, not co-linear, not intersecting
        (Segment(Point2D(-1, 2), Point2D(1, 2)), (Point2D(0, 2), None)), # not parallel, co-linear, middle-end
        (Segment(Point2D(-1, 1), Point2D(1, 1)), (Point2D(0, 1), Point2D(0, 1))), # not parallel, not co-linear, middle-middle
        (Segment(Point2D(0, 3), Point2D(2, 3)), (None, None)), # not parallel, not co-linear, not intersecting
        (Segment(Point2D(0, 2), Point2D(2, 2)), (Point2D(0, 2), None)), # not parallel, co-linear, end-end
        (Segment(Point2D(0, 1), Point2D(2, 1)), (Point2D(0, 1), None)), # not parallel, co-linear, middle-end
    ]
    segment1 = Segment(Point2D(0, 0), Point2D(0, 2))
    for segment2, expecteds in segments:
        for expected, include_end in zip(expecteds, (True, False)):
            answer12 = segment1.intersect(segment2, include_end=include_end)
            answer21 = segment2.intersect(segment1, include_end=include_end)
            if expected is None:
                assert answer12 is None
                assert answer21 is None
            else:
                assert answer12 is not None
                assert answer21 is not None
                assert answer12 == expected
                assert answer21 == expected
    # more than one point of intersection
    segment2 = Segment(Point2D(0, 1), Point2D(0, 3))
    for answer in [segment1.intersect(segment2), segment2.intersect(segment1)]:
        assert answer.x == 0 and 1 <= answer.y <= 2
    segment2 = Segment(Point2D(0, 0), Point2D(0, 2))
    for answer in [segment1.intersect(segment2), segment2.intersect(segment1)]:
        assert answer.x == 0 and 0 <= answer.y <= 2
    # bounding box intersects but not segments
    segment1 = Segment(Point2D(0, 4), Point2D(4, 0))
    segment2 = Segment(Point2D(0, 0), Point2D(1, 1))
    assert segment1.intersect(segment2) is None
    assert segment2.intersect(segment1) is None


def _no_duplicates_coord_segments(num_segments):
    # type: (int) -> Iterator[tuple[Segment, ...]]
    """Generate segments with no duplicate x or y coordinates."""

    def _generate_segments(xs, ys):
        # type: (list[int], list[int]) -> Iterator[tuple[Segment, ...]]
        if not xs:
            yield ()
            return
        x1 = xs[0]
        for y1 in ys:
            point1 = Point2D(x1, y1)
            xs_ = xs[1:]
            ys_ = [y for y in ys if y != y1]
            for x2, y2 in product(xs_, ys_):
                recursed = _generate_segments(
                    [x for x in xs_ if x != x2],
                    [y for y in ys_ if y != y2],
                )
                segment = Segment(point1, Point2D(x2, y2))
                for segments in recursed:
                    yield (segment, *segments)

    yield from _generate_segments(
        list(range(2 * num_segments)),
        list(range(2 * num_segments)),
    )


def _naive_all_intersects(segments, include_end=False):
    # type: (Sequence[Segment], bool) -> list[Matrix]
    """Calculate all intersects naively (in O(n^2) time)."""
    results = []
    for i, segment1 in enumerate(segments):
        for segment2 in segments[i + 1:]:
            intersect = segment1.intersect(segment2, include_end=include_end)
            if intersect is not None:
                results.append(intersect)
    return results


def test_bentley_ottmann():
    # type: () -> None
    """Testing entry point."""

    def test_segments(segments, include_end):
        # type: (Sequence[Segment], bool) -> None
        for segment1, segment2 in combinations(segments, 2):
            if segment1.is_overlapping(segment2):
                return
        # do the test
        expected = sorted(set(
            round(intersect, 3).to_tuple()[0][:2] for intersect
            in _naive_all_intersects(segments, include_end=include_end)
        ))
        actual = sorted(
            round(intersect, 3).to_tuple()[0][:2] for intersect
            in bentley_ottmann(segments, include_end=include_end)
        )
        assert expected == actual, (segments, expected, actual)

    # no duplicate x or y, including three-segment intersects
    num_segments = 3
    for segments in _no_duplicates_coord_segments(num_segments):
        for include_end in (False, True):
            test_segments(segments, include_end)
    # vertical segment with one horizontal segment
    assert bentley_ottmann([
        Segment(Point2D(-2, 1), Point2D(2, 1)),
        Segment(Point2D(1, -2), Point2D(1, 2)),
    ]) == [Point2D(1, 1)]
    # vertical segment with multiple horizontal segments
    assert bentley_ottmann([
        Segment(Point2D(0, -3), Point2D(0, 3)),
        *(
            Segment(Point2D(-3, i), Point2D(3, i))
            for i in range(-2, 3)
        )
    ]) == [Point2D(0, i) for i in range(-2, 3)]
    # vertical segment that "kisses" a horizontal segment
    for include_end, expected in zip((False, True), ([], [Point2D(0, 0)])):
        assert bentley_ottmann(
            [
                Segment(Point2D(-2, 0), Point2D(0, 0)),
                Segment(Point2D(0, -2), Point2D(0, 2)),
            ],
            include_end=include_end,
        ) == expected
    # non-vertical co-linear segments that "kiss"
    for include_end, expected in zip((False, True), ([], [Point2D(0, 0)])):
        assert bentley_ottmann(
            [
                Segment(Point2D(-2, -2), Point2D(0, 0)),
                Segment(Point2D(0, 0), Point2D(2, 2)),
            ],
            include_end=include_end,
        ) == expected
    # vertical co-linear segments that "kiss"
    for include_end, expected in zip((False, True), ([], [Point2D(0, 0)])):
        assert bentley_ottmann(
            [
                Segment(Point2D(0, -2), Point2D(0, 0)),
                Segment(Point2D(0, 0), Point2D(0, 2)),
            ],
            include_end=include_end,
        ) == expected
