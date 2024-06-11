"""Tests for color.py."""

from dumpy.color import Color


def test_color():
    """Test Color."""
    color = Color.from_hex('#73D21680')
    assert color.to_rgb_hex() == '#73D216'
    assert color.to_rgba_hex() == '#73D21680'
    assert color.to_rgba_tuple() == (115, 210, 22, 128)
    assert color.to_rgb_tuple() == (115, 210, 22)
    assert Color.from_rgba(115/256, 210/256, 22/256, 128/256) == color
    assert color.to_hsva_tuple() == (135, 97, 84, 128)
    assert Color(0.25, 0.5, 0.75, 0).to_hsva_tuple(integer=False) == (0.25, 0.5, 0.75, 0)
    assert str(Color(0.25, 0.5, 0.75, 0)) == 'Color(0.25, 0.5, 0.75, 0)'
    assert tuple(color) == (135, 97, 84, 128)
    assert Color.from_hex('#000000').to_rgb_tuple() == (0, 0, 0)
