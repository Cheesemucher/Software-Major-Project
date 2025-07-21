import pytest
from utils.shapes import *
import math

@pytest.mark.parametrize("shape_type, expected_type", [
    ("square", "square"),
    ("triangle", "triangle"),
])
def test_shape_type_selection(shape_type, expected_type):
    result = handle_place_shape_request({"type": shape_type, "x": 100, "y": 100, "rotation": 0}, [])
    assert result["placed"][0]["type"] == expected_type

def test_shape_square_location_zero_rotation():
    click_x, click_y, rotation = 100, 100, 0
    result = handle_place_shape_request({"type": "square", "x": click_x, "y": click_y, "rotation": rotation}, [])
    expected = get_square_centre(click_x, click_y, rotation)
    assert result["placed"][0]["x"] == expected["x"]
    assert result["placed"][0]["y"] == expected["y"]

def test_shape_triangle_location_zero_rotation():
    click_x, click_y, rotation = 200, 200, 0
    result = handle_place_shape_request({"type": "triangle", "x": click_x, "y": click_y, "rotation": rotation}, [])
    expected = get_triangle_centre(click_x, click_y, rotation)
    assert result["placed"][0]["x"] == expected["x"]
    assert result["placed"][0]["y"] == expected["y"]
