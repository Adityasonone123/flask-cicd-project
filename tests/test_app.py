import unittest
import sys
import os

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app

class FlaskTestCase(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_home(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Hello from CI/CD Pipeline with Flask!', response.data)
    
    def test_home_response_type(self):
        response = self.app.get('/')
        self.assertEqual(response.content_type, 'text/html; charset=utf-8')

if __name__ == '__main__':
    unittest.main()
