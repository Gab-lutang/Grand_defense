import time
import requests
import json

def test_server_connection():
	"""Test if server is running"""
	try:
		response = requests.get('http://localhost:5000/api/status')
		print("Server Connection:", "OK" if response.status_code == 200 else "Failed")
		return response.status_code == 200
	except:
		print("Server Connection: Failed - Is server running?")
		return False

def test_phone_update(phone_number):
	"""Test phone number update"""
	try:
		response = requests.post('http://localhost:5000/api/phone',
			json={'phone': phone_number})
		print(f"Phone Update ({phone_number}):", 
			"Success" if response.status_code == 200 else f"Failed - {response.json().get('error')}")
	except Exception as e:
		print(f"Phone Update Error: {str(e)}")

def monitor_status(duration=30):
	"""Monitor status for specified duration"""
	print(f"\nMonitoring status for {duration} seconds...")
	start_time = time.time()
	while time.time() - start_time < duration:
		try:
			response = requests.get('http://localhost:5000/api/status')
			data = response.json()
			print("\nStatus Update:")
			print(f"Fire Detected: {data.get('fire_detected', False)}")
			print(f"Gas Detected: {data.get('gas_detected', False)}")
			print(f"SMS Balance: {data.get('sms_balance', 0)}")
			time.sleep(3)
		except Exception as e:
			print(f"Monitoring Error: {str(e)}")
			break

def run_manual_tests():
	"""Run interactive manual tests"""
	print("=== Fire Alarm System Manual Tests ===\n")
	
	if not test_server_connection():
		return
	
	# Test phone number update
	print("\nTesting phone number update...")
	test_phone_update("+639123456789")  # Valid number
	test_phone_update("1234567890")     # Invalid number
	
	# Monitor system
	monitor_status()

if __name__ == "__main__":
	run_manual_tests()