
from context import tracker

import math


def test_fov_90_degrees():
    assert 90 == tracker.field_of_view(size=2, distance=1)


def test_fov_60_degrees():
    fov = tracker.field_of_view(size=1, distance=math.sqrt(3)/2)
    assert 60 == round(fov, 9)  # floating-point limitation


def test_fov_extreme_wide():
    assert 170 < tracker.field_of_view(size=100, distance=0.01)


def test_fov_zero_distance():
    assert 180 == tracker.field_of_view(1, 0)
