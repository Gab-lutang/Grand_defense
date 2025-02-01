import time
import requests
import json
import sys
import os

# Add parent directory to path to import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_server_connection():
	"""Test if server is running"""
	try:
		response = requests.get('http://localhost:5000/api/status')
		print("Server Connection:", "OK" if response.status_code == 200 else "Failed")
		return response.status_code == 200
	except:
		print("Server Connection: Failed - Is server running?")
		return False

def monitor_status():
	"""Monitor system status continuously"""
	print("\nMonitoring system status. Press Ctrl+C to exit.")
	print("-" * 50)
	
	try:
		while True:
			response = requests.get('http://localhost:5000/api/status')
			data = response.json()
			
			print("\nStatus Update:")
			print("Fire Detected:", data['fire_detected'])
			print("Gas Detected:", data['gas_detected'])
			print("SMS Balance:", data['sms_balance'])
			print("-" * 30)
			
			time.sleep(3)
	except KeyboardInterrupt:
		print("\nMonitoring stopped by user")
	except Exception as e:
		print(f"\nError occurred: {e}")

def run_manual_tests():
	"""Run all manual tests"""
	print("Starting Manual Tests...")
	print("-" * 50)
	
	# Test server connection
	if not test_server_connection():
		print("Aborting tests due to server connection failure")
		return
	
	# Monitor system
	monitor_status()

if __name__ == "__main__":
	run_manual_tests()