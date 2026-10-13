"""Tests for choose_compartment_layout."""

from momapy.geometry import Point
from momapy.io._utils import choose_compartment_layout
from momapy.meta.nodes import Rectangle


def test_single_layout_is_returned():
    layout = Rectangle(position=Point(0.0, 0.0), width=10.0, height=10.0)
    assert choose_compartment_layout([layout], Point(500.0, 500.0)) is layout


def test_smallest_containing_layout_is_chosen():
    large = Rectangle(position=Point(0.0, 0.0), width=100.0, height=100.0)
    small = Rectangle(position=Point(10.0, 10.0), width=20.0, height=20.0)
    assert choose_compartment_layout([large, small], Point(10.0, 10.0)) is small


def test_nearest_layout_is_chosen_when_none_contains_the_point():
    near = Rectangle(position=Point(0.0, 0.0), width=10.0, height=10.0)
    far = Rectangle(position=Point(100.0, 0.0), width=10.0, height=10.0)
    assert choose_compartment_layout([far, near], Point(20.0, 0.0)) is near
