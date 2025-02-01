import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os

# Add parent directory to path to import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from server import app

class TestFireAlarmServer(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.addCleanup(self.cleanup)
	
	def cleanup(self):
		import gc
		gc.collect()
	
	@patch('server.arduino')
	def test_get_status_no_arduino(self, mock_arduino):
		"""Test status endpoint when Arduino is not connected"""
		mock_arduino.connected = False
		
		response = self.app.get('/api/status')
		data = json.loads(response.data)
		
		self.assertEqual(response.status_code, 200)
		self.assertFalse(data['fire_detected'])
		self.assertFalse(data['gas_detected'])
		self.assertEqual(data['sms_balance'], 0)

def run_tests():
	"""Run all tests and print results"""
	print("Starting Fire Alarm Server Tests...")
	print("-" * 50)
	unittest.main(verbosity=2)

if __name__ == '__main__':
	run_tests()