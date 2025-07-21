# Test cases
from utils.shapes import *
import math

def approx_equal(a, b, tol=0.01):
    return abs(a - b) <= tol


def test_get_square_centre():
    centre = get_square_centre(100, 100, 0)
    assert approx_equal(centre["x"], 100)
    assert approx_equal(centre["y"], 60)

    centre = get_square_centre(100, 100, 90)
    assert approx_equal(centre["x"], 140)
    assert approx_equal(centre["y"], 100)


def test_get_triangle_centre():
    height = math.sqrt(3) / 2 * TILE_SIDE_LENGTH
    expected_y = 100 - (height / 3)

    centre = get_triangle_centre(100, 100, 0)
    assert approx_equal(centre["x"], 100)
    assert approx_equal(centre["y"], expected_y)


def test_get_square_edge_positions():
    centre = {"x": 100, "y": 100}
    edges = get_square_edge_positions(centre, 0)
    assert len(edges) == 4
    for edge in edges:
        assert isinstance(edge["x"], float)
        assert isinstance(edge["y"], float)
        assert isinstance(edge["rotation"], float)


def test_get_triangle_edge_positions():
    centre = {"x": 100, "y": 100}
    edges = get_triangle_edge_positions(centre, 0)
    assert len(edges) == 3
    for edge in edges:
        assert isinstance(edge["x"], float)
        assert isinstance(edge["y"], float)
        assert isinstance(edge["rotation"], float)


def test_check_overlap():
    s1 = {"x": 100, "y": 100, "type": "square"}
    s2 = {"x": 120, "y": 100, "type": "square"}
    assert check_overlap(s1, s2)

    s3 = {"x": 200, "y": 200, "type": "square"}
    assert not check_overlap(s1, s3)

