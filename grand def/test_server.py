import unittest
from unittest.mock import patch, MagicMock
import json
from server import app

class TestFireAlarmServer(unittest.TestCase):
	def setUp(self):
		self.app = app.test_client()
		self.app.testing = True
		self.addCleanup(self.cleanup)
	
	def cleanup(self):
		# Force garbage collection to clean up any lingering file handles
		import gc
		gc.collect()
	
	def test_home_page(self):
		"""Test if home page is served correctly"""
		with self.app.get('/') as response:
			self.assertEqual(response.status_code, 200)
			self.assertIn(b'Fire Alarm Monitor', response.data)

	def test_status_endpoint_no_arduino(self):
		"""Test status endpoint when Arduino is not connected"""
		with self.app.get('/api/status') as response:
			data = json.loads(response.data)
			
			self.assertEqual(response.status_code, 200)
			self.assertFalse(data['fire_detected'])
			self.assertIn('timestamp', data)
			self.assertEqual(type(data['timestamp']), float)

	@patch('server.arduino')
	def test_status_endpoint_with_arduino(self, mock_arduino):
		"""Test status endpoint with mocked Arduino data"""
		# Mock Arduino response
		mock_arduino.readline.return_value = json.dumps({
			'fire_detected': True,
			'gas_detected': True,
			'sms_balance': 50
		}).encode()

		with self.app.get('/api/status') as response:
			data = json.loads(response.data)
			
			self.assertEqual(response.status_code, 200)
			self.assertTrue(data['fire_detected'])
			self.assertTrue(data['gas_detected'])
			self.assertEqual(data['sms_balance'], 50)

	def test_update_phone_invalid_format(self):
		"""Test phone number update with invalid format"""
		with self.app.post('/api/phone', 
			json={'phone': '1234567890'}) as response:
			
			self.assertEqual(response.status_code, 400)
			data = json.loads(response.data)
			self.assertIn('error', data)
			self.assertEqual(data['error'], 'Invalid phone number format')

	@patch('server.arduino')
	def test_update_phone_valid(self, mock_arduino):
		"""Test phone number update with valid format"""
		# Mock Arduino response
		mock_arduino.readline.return_value = json.dumps({
			'phone_updated': '+639123456789'
		}).encode()

		with self.app.post('/api/phone', 
			json={'phone': '+639123456789'}) as response:
			
			self.assertEqual(response.status_code, 200)
			data = json.loads(response.data)
			self.assertEqual(data['phone_updated'], '+639123456789')

	def test_missing_phone_number(self):
		"""Test phone update with missing phone number"""
		with self.app.post('/api/phone', json={}) as response:
			self.assertEqual(response.status_code, 400)
			data = json.loads(response.data)
			self.assertEqual(data['error'], 'Phone number required')


	@patch('server.arduino')
	def test_arduino_communication_error(self, mock_arduino):
		"""Test handling of Arduino communication error"""
		mock_arduino.write.side_effect = Exception('Communication error')
		
		with self.app.post('/api/phone', 
			json={'phone': '+639123456789'}) as response:
			
			self.assertEqual(response.status_code, 500)
			data = json.loads(response.data)
			self.assertIn('error', data)

	@patch('server.arduino')
	def test_gas_detection(self, mock_arduino):
		"""Test gas detection status"""
		# Mock Arduino response with gas detection
		mock_arduino.readline.return_value = json.dumps({
			'fire_detected': False,
			'gas_detected': True,
			'sms_balance': 50
		}).encode()

		with self.app.get('/api/status') as response:
			data = json.loads(response.data)
			
			self.assertEqual(response.status_code, 200)
			self.assertFalse(data['fire_detected'])
			self.assertTrue(data['gas_detected'])

	@patch('server.arduino')
	def test_sms_balance_update(self, mock_arduino):
		"""Test SMS balance updates correctly"""
		# Mock initial balance
		mock_arduino.readline.return_value = json.dumps({
			'fire_detected': False,
			'gas_detected': False,
			'sms_balance': 75
		}).encode()

		with self.app.get('/api/status') as response:
			data = json.loads(response.data)
			
			self.assertEqual(response.status_code, 200)
			self.assertEqual(data['sms_balance'], 75)

	def test_arduino_connection_failure(self):
		"""Test system behavior when Arduino connection fails"""
		with patch('server.arduino', None):
			with self.app.get('/api/status') as response:
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