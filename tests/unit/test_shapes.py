"""
Unit tests for shape calculation utilities
"""

import unittest
import math
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from utils.shapes import (
    get_square_centre, get_triangle_centre,
    get_square_edge_positions, get_triangle_edge_positions,
    check_overlap, TILE_SIDE_LENGTH
)


class TestShapeCalculations(unittest.TestCase):
    
    def test_square_centre_calculation(self):
        """Test square centre calculation from edge point"""
        # Click at origin with 0 rotation (upward)
        centre = get_square_centre(0, 0, 0)
        self.assertEqual(centre["x"], 0)
        self.assertEqual(centre["y"], -40)
        
        # Click with 90 degree rotation (rightward)
        centre = get_square_centre(0, 0, 90)
        self.assertEqual(centre["x"], 40)
        self.assertEqual(centre["y"], 0)
    
    def test_triangle_centre_calculation(self):
        """Test triangle centre calculation from edge point"""
        height = math.sqrt(3)/2 * TILE_SIDE_LENGTH
        expected_dist = height / 3
        
        # Click at origin with 0 rotation
        centre = get_triangle_centre(0, 0, 0)
        self.assertEqual(centre["x"], 0)
        self.assertAlmostEqual(centre["y"], -expected_dist, places=2)
        
        # Click with 90 degree rotation
        centre = get_triangle_centre(0, 0, 90)
        self.assertAlmostEqual(centre["x"], expected_dist, places=2)
        self.assertAlmostEqual(centre["y"], 0, places=2)
    
    def test_square_edge_positions(self):
        """Test calculation of square edge positions"""
        centre = {"x": 100, "y": 100}
        edges = get_square_edge_positions(centre, 0)
        
        self.assertEqual(len(edges), 4)
        
        # Check distances from centre
        for edge in edges:
            dist = math.sqrt((edge["x"] - centre["x"])**2 + 
                           (edge["y"] - centre["y"])**2)
            self.assertAlmostEqual(dist, 40, places=2)
    
    def test_triangle_edge_positions(self):
        """Test calculation of triangle edge positions"""
        centre = {"x": 100, "y": 100}
        edges = get_triangle_edge_positions(centre, 0)
        
        # Should only return 2 edges (not the base)
        self.assertEqual(len(edges), 2)
        
        # Check distances from centre
        height = math.sqrt(3)/2 * TILE_SIDE_LENGTH
        expected_dist = height / 3
        
        for edge in edges:
            dist = math.sqrt((edge["x"] - centre["x"])**2 + 
                           (edge["y"] - centre["y"])**2)
            self.assertAlmostEqual(dist, expected_dist, places=2)
    
    def test_overlap_detection_squares(self):
        """Test overlap detection between squares"""
        square1 = {"x": 0, "y": 0, "type": "square"}
        square2 = {"x": 50, "y": 0, "type": "square"}
        square3 = {"x": 80, "y": 0, "type": "square"}
        
        # Too close - should overlap
        self.assertTrue(check_overlap(square1, square2))
        
        # Edge to edge - should not overlap
        self.assertFalse(check_overlap(square1, square3))
    
    def test_overlap_detection_triangles(self):
        """Test overlap detection between triangles"""
        tri1 = {"x": 0, "y": 0, "type": "triangle"}
        tri2 = {"x": 30, "y": 0, "type": "triangle"}
        tri3 = {"x": 40, "y": 0, "type": "triangle"}
        
        # Too close - should overlap
        self.assertTrue(check_overlap(tri1, tri2))
        
        # Edge to edge - should not overlap
        self.assertFalse(check_overlap(tri1, tri3))
    
    def test_overlap_detection_mixed(self):
        """Test overlap detection between square and triangle"""
        square = {"x": 0, "y": 0, "type": "square"}
        tri_close = {"x": 50, "y": 0, "type": "triangle"}
        tri_far = {"x": 65, "y": 0, "type": "triangle"}
        
        # Too close - should overlap
        self.assertTrue(check_overlap(square, tri_close))
        
        # Far enough - should not overlap
        self.assertFalse(check_overlap(square, tri_far))


if __name__ == '__main__':
    unittest.main()