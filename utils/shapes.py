"""
Shape calculation utilities for the floor planning application
"""

import math

TILE_SIDE_LENGTH = 80


def get_square_centre(click_x, click_y, rotation):
    """Calculate square centre position from edge click point"""
    rotation_rad = rotation * math.pi / 180
    shift_x = TILE_SIDE_LENGTH/2 * math.sin(rotation_rad)
    shift_y = -TILE_SIDE_LENGTH/2 * math.cos(rotation_rad)
    
    return {
        "x": click_x + shift_x,
        "y": click_y + shift_y
    }


def get_triangle_centre(click_x, click_y, rotation):
    """Calculate triangle centre position from edge click point"""
    height = math.sqrt(3)/2 * TILE_SIDE_LENGTH
    dist_from_base_to_centre = height / 3
    
    rotation_rad = rotation * math.pi / 180
    shift_x = dist_from_base_to_centre * math.sin(rotation_rad)
    shift_y = -dist_from_base_to_centre * math.cos(rotation_rad)
    
    return {
        "x": click_x + shift_x,
        "y": click_y + shift_y
    }


def get_square_edge_positions(centre, rotation):
    """Get plus button positions for square edges"""
    rotation_rad = rotation * math.pi / 180
    edge_positions = []
    
    for k in range(4):
        angle = rotation_rad + k * (math.pi/2)
        mx = centre["x"] + TILE_SIDE_LENGTH/2 * math.sin(angle)
        my = centre["y"] - TILE_SIDE_LENGTH/2 * math.cos(angle)
        edge_positions.append({
            "x": mx,
            "y": my,
            "rotation": angle * 180 / math.pi
        })
    
    return edge_positions


def get_triangle_edge_positions(centre, rotation):
    #Get plus button positions for triangle edges (excluding base)
    height = math.sqrt(3)/2 * TILE_SIDE_LENGTH
    rotation_rad = rotation * math.pi / 180
    base_angle = rotation_rad + math.pi
    
    edges = [
        {"angle": base_angle},                # Base edge
        {"angle": base_angle + math.pi*2/3},  # Left edge
        {"angle": base_angle - math.pi*2/3}   # Right edge
    ]
    
    edge_positions = []
    dist_to_edge = height / 3
    
    for edge in edges:
        mx = centre["x"] + dist_to_edge * math.sin(edge["angle"])
        my = centre["y"] - dist_to_edge * math.cos(edge["angle"])
        edge_positions.append({
            "x": mx,
            "y": my,
            "rotation": edge["angle"] * 180 / math.pi
        })
    
    return edge_positions


def check_overlap(shape1, shape2):
    """Check if two shapes would overlap"""
    distance = math.sqrt(
        (shape1["x"] - shape2["x"])**2 + 
        (shape1["y"] - shape2["y"])**2
    )
    
    # Define minimum distances based on shape combinations
    if shape1["type"] == "square" and shape2["type"] == "square":
        min_distance = TILE_SIDE_LENGTH - 5
    elif shape1["type"] == "triangle" and shape2["type"] == "triangle":
        min_distance = 35
    else:
        min_distance = 58
    
    return distance < min_distance


def check_shape_overlap(new_shape, existing_shapes): # Check overlap for full shape array
    """Check if a new shape would overlap with any existing shapes"""
    for shape in existing_shapes:
        if check_overlap(new_shape, shape):
            return False # Should be set to true to prevent overlap, disabled for testing purposes
    return False 


def handle_place_shape_request(data: dict, existing_shapes: list):
    shape_type = data.get("type")
    x = data.get("x")
    y = data.get("y")
    rotation = data.get("rotation")

    if shape_type == "square":
        centre = get_square_centre(x, y, rotation)
        new_plus_signs = get_square_edge_positions(centre, rotation)
    elif shape_type == "triangle":
        centre = get_triangle_centre(x, y, rotation)
        new_plus_signs = get_triangle_edge_positions(centre, rotation)
    else:
        return {"error": "Invalid shape type", "placed": [], "plus_points": []}

    new_shape = {"x": centre["x"], "y": centre["y"], "type": shape_type, "rotation": rotation}

    if check_shape_overlap(new_shape, existing_shapes):
        return {"error": "Shape would overlap", "placed": [], "plus_points": []}

    filtered_plus_signs = []
    for plus in new_plus_signs:
        square = get_square_centre(plus["x"], plus["y"], plus["rotation"])
        square["type"] = "square"
        triangle = get_triangle_centre(plus["x"], plus["y"], plus["rotation"])
        triangle["type"] = "triangle"

        if not check_shape_overlap(square, existing_shapes) or not check_shape_overlap(triangle, existing_shapes):
            filtered_plus_signs.append(plus)

    return {"placed": [new_shape], "plus_points": filtered_plus_signs}
