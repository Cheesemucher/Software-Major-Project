"""
Integration tests for the Flask application
"""

import unittest
import json
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app import app


class TestFlaskApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()
    
    def test_home_redirect(self):
        """Test that home page redirects to login"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login'))
    
    def test_login_page(self):
        """Test login page loads correctly"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_build_page(self):
        """Test build page loads correctly"""
        response = self.client.get('/build')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Build', response.data)
    
    def test_place_square(self):
        """Test placing a square shape"""
        # Clear any existing shapes
        with self.client.session_transaction() as sess:
            sess['placed_shapes'] = []
        
        # Place a square
        response = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'square',
                'size': 80,
                'x': 400,
                'y': 300,
                'rotation': 0
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check that shape was placed
        self.assertEqual(len(data['placed']), 1)
        self.assertEqual(data['placed'][0]['type'], 'square')
        
        # Check that plus points were generated
        self.assertEqual(len(data['plus_points']), 4)
    
    def test_place_triangle(self):
        """Test placing a triangle shape"""
        with self.client.session_transaction() as sess:
            sess['placed_shapes'] = []
        
        response = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'triangle',
                'size': 80,
                'x': 400,
                'y': 300,
                'rotation': 0
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Check that shape was placed
        self.assertEqual(len(data['placed']), 1)
        self.assertEqual(data['placed'][0]['type'], 'triangle')
        
        # Check that plus points were generated (only 2 for triangle)
        self.assertEqual(len(data['plus_points']), 2)
    
    def test_collision_detection(self):
        """Test that collision detection prevents overlapping shapes"""
        with self.client.session_transaction() as sess:
            sess['placed_shapes'] = []
        
        # Place first square
        response1 = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'square',
                'size': 80,
                'x': 400,
                'y': 300,
                'rotation': 0
            }),
            content_type='application/json'
        )
        self.assertEqual(response1.status_code, 200)
        
        # Try to place overlapping square
        response2 = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'square',
                'size': 80,
                'x': 410,  # Too close
                'y': 310,
                'rotation': 0
            }),
            content_type='application/json'
        )
        
        data = json.loads(response2.data)
        self.assertIn('error', data)
        self.assertEqual(len(data['placed']), 0)
    
    def test_edge_to_edge_placement(self):
        """Test that shapes can be placed edge-to-edge"""
        with self.client.session_transaction() as sess:
            sess['placed_shapes'] = []
        
        # Place first square
        response1 = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'square',
                'size': 80,
                'x': 400,
                'y': 300,
                'rotation': 0
            }),
            content_type='application/json'
        )
        
        data1 = json.loads(response1.data)
        # Get the right edge plus button
        right_plus = next(p for p in data1['plus_points'] if p['rotation'] == 90)
        
        # Place second square at the edge
        response2 = self.client.post('/place-shape',
            data=json.dumps({
                'type': 'square',
                'size': 80,
                'x': right_plus['x'],
                'y': right_plus['y'],
                'rotation': right_plus['rotation']
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response2.status_code, 200)
        data2 = json.loads(response2.data)
        self.assertEqual(len(data2['placed']), 1)


if __name__ == '__main__':
    unittest.main()