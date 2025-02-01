from flask import Flask, jsonify, send_from_directory, request
from flask_cors import CORS
import serial
import json
import time
import os

# Get the directory containing the script
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
CORS(app)

# Initialize serial connection with Arduino
try:
	arduino = serial.Serial('COM3', 9600, timeout=1)  # Change COM3 to your Arduino port
	print("Connected to Arduino")
except:
	arduino = None
	print("Failed to connect to Arduino, running in simulation mode")

@app.route('/')
def serve_index():
	try:
		return send_from_directory(current_dir, 'index.html')
	finally:
		# Force garbage collection to ensure file handles are released
		import gc
		gc.collect()

@app.route('/api/phone', methods=['POST'])
def update_phone():
	if not arduino:
		return jsonify({'error': 'Arduino not connected'}), 400
	
	data = request.get_json()
	if not data or 'phone' not in data:
		return jsonify({'error': 'Phone number required'}), 400
	
	phone = data['phone']
	# Validate phone number format (basic validation)
	if not phone.startswith('+') or not phone[1:].isdigit():
		return jsonify({'error': 'Invalid phone number format'}), 400
	
	try:
		arduino.write(f'PHONE:{phone}\n'.encode())
		response = arduino.readline().decode('utf-8').strip()
		return jsonify(json.loads(response))
	except Exception as e:
		return jsonify({'error': str(e)}), 500

@app.route('/api/status')
def get_status():
	if arduino:
		try:
			# Read data from Arduino
			line = arduino.readline().decode('utf-8').strip()
			if line:
				data = json.loads(line)
				data['timestamp'] = time.time()
				return jsonify(data)
		except Exception as e:
			print(f"Error reading from Arduino: {e}")
	
	# Fallback to simulation if Arduino read fails or not connected
	return jsonify({
		'fire_detected': False,
		'gas_detected': False,
		'sms_balance': 0,
		'timestamp': time.time()
	})

@app.route('/api/load', methods=['POST'])
def update_load():
	if not arduino:
		return jsonify({'error': 'Arduino not connected'}), 400
	
	data = request.get_json()
	if not data or 'load_used' not in data:
		return jsonify({'error': 'Load value required'}), 400
	
	load_used = data['load_used']
	# Validate load value
	if not isinstance(load_used, (int, float)) or load_used < 0 or load_used > 100:
		return jsonify({'error': 'Invalid load value. Must be between 0 and 100'}), 400
	
	try:
		arduino.write(f'LOAD:{load_used}\n'.encode())
		response = arduino.readline().decode('utf-8').strip()
		return jsonify(json.loads(response))
	except Exception as e:
		return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
	app.run(port=5000, debug=True)